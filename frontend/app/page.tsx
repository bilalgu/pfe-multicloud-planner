'use client';

import { useState, useEffect } from 'react';
import ErrorToast from './components/ErrorToast';
import SuccessToast from './components/SuccessToast';
import LoadingSpinner from './components/LoadingSpinner';

interface ProviderConfig {
  provider: string;
  servers: number;
  databases: number;
  networks: number;
  load_balancers: number;
  security_groups: number;
}

interface InfrastructureResult {
  success: boolean;
  infrastructure: {
    providers: ProviderConfig[];
  };
  terraform_code: string;
  message: string;
  security_report?: {
    violations: Array<{
      rule: string;
      severity: string;
      message: string;
      recommendation: string;
    }>;
    dangerous_requests?: Array<{
      requested: string;
      reason: string;
      applied: string;
    }>;
    total_issues: number;
    security_score: number;
  };
}

export default function Home() {
  const [need, setNeed] = useState('');
  const [result, setResult] = useState<InfrastructureResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [toast, setToast] = useState<{ type: 'success' | 'error'; message: string } | null>(null);
  const [selectedProvider, setSelectedProvider] = useState<string>('all');

  // Auto-close toast après 5 secondes
  useEffect(() => {
    if (toast) {
      const timer = setTimeout(() => setToast(null), 5000);
      return () => clearTimeout(timer);
    }
  }, [toast]);

  // ────────────────────────────────────────────────
  // Parser des sections par provider
  // ────────────────────────────────────────────────
  const extractProviderSections = (code: string) => {
    const sections: Record<string, string> = {};
    let currentProvider: string | null = null;
    let currentLines: string[] = [];

    const lines = code.split('\n');

    for (const line of lines) {
      const trimmed = line.trim();
      if (trimmed.startsWith('# SECTION ')) {
        // Sauvegarde section précédente
        if (currentProvider && currentLines.length > 0) {
          sections[currentProvider.toLowerCase()] = currentLines.join('\n').trim();
        }
        currentProvider = trimmed.replace('# SECTION ', '').trim();
        currentLines = [];
      } else if (currentProvider !== null) {
        currentLines.push(line);
      }
    }

    // Dernière section
    if (currentProvider && currentLines.length > 0) {
      sections[currentProvider.toLowerCase()] = currentLines.join('\n').trim();
    }

    // Si aucune section → tout dans 'all'
    if (Object.keys(sections).length === 0 && code.trim()) {
      sections['all'] = code.trim();
    }

    return sections;
  };

  const terraformSections = result?.terraform_code
    ? extractProviderSections(result.terraform_code)
    : {};

  const providerKeys = Object.keys(terraformSections).filter(key => key !== 'all');
  const hasMultipleProviders = providerKeys.length > 1;
  const displayKey = hasMultipleProviders ? selectedProvider : 'all';

  const getDisplayCode = () => {
    if (!result?.terraform_code) return '';
    return terraformSections[displayKey] || result.terraform_code;
  };

  const copyToClipboard = () => {
    const code = getDisplayCode();
    if (code) {
      navigator.clipboard.writeText(code)
        .then(() => setToast({ type: 'success', message: 'Code copié !' }))
        .catch(() => setToast({ type: 'error', message: 'Erreur lors de la copie' }));
    }
  };

  const downloadTerraform = () => {
    const code = getDisplayCode();
    if (code && code !== 'BLOCKED') {
      const blob = new Blob([code], { type: 'text/plain;charset=utf-8' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `terraform-${displayKey !== 'all' ? displayKey.toUpperCase() : 'multi'}.tf`;
      link.click();
      URL.revokeObjectURL(url);
      setToast({ type: 'success', message: 'Fichier téléchargé !' });
    }
  };

  const handleGenerate = async () => {
    if (!need.trim()) {
      setToast({ type: 'error', message: 'Décris ton besoin !' });
      return;
    }

    setLoading(true);
    setError('');
    setResult(null);
    setSelectedProvider('all');

    try {
      const response = await fetch('/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ description: need }),
      });

      if (!response.ok) throw new Error('Erreur serveur');

      const data = await response.json();
      setResult(data);

      if (data.success) {
        setToast({ type: 'success', message: 'Génération terminée !' });
      } else {
        setToast({ type: 'error', message: 'Génération bloquée (sécurité)' });
      }
    } catch (err: any) {
      const msg = err.message || 'Erreur inattendue';
      setError(msg);
      setToast({ type: 'error', message: msg });
    } finally {
      setLoading(false);
    }
  };

  // Stats agrégées (inchangé)
  const getAggregatedStats = () => {
    if (!result?.infrastructure?.providers) return null;
    const providers = result.infrastructure.providers;
    const providerNames = providers.map(p => p.provider.toUpperCase()).join(' + ');
    return {
      providerNames,
      totalServers: providers.reduce((s, p) => s + p.servers, 0),
      totalDatabases: providers.reduce((s, p) => s + p.databases, 0),
      totalNetworks: providers.reduce((s, p) => s + p.networks, 0),
      totalLBs: providers.reduce((s, p) => s + p.load_balancers, 0),
      totalSGs: providers.reduce((s, p) => s + p.security_groups, 0),
    };
  };

  const stats = getAggregatedStats();

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 p-8">
      {toast && (
        toast.type === 'error' ? (
          <ErrorToast message={toast.message} onClose={() => setToast(null)} />
        ) : (
          <SuccessToast message={toast.message} onClose={() => setToast(null)} />
        )
      )}

      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Planificateur d'architectures sécurisées multi-cloud
        </h1>
        <p className="text-xl text-gray-600 mb-10">
          Décris ton besoin en langage naturel et on génère Terraform sécurisé
        </p>

        <textarea
          value={need}
          onChange={(e) => setNeed(e.target.value)}
          placeholder="Exemple : 3 serveurs web sur AWS + stockage sur GCP"
          className="w-full h-64 p-6 text-lg border-2 border-gray-300 rounded-xl focus:border-blue-600 focus:outline-none resize-none font-mono"
          disabled={loading}
        />

        <button
          onClick={handleGenerate}
          disabled={loading || !need.trim()}
          className="mt-8 px-12 py-5 bg-blue-600 hover:bg-blue-700 text-white text-xl font-semibold rounded-xl shadow-lg transition transform hover:scale-105 disabled:bg-gray-400 disabled:cursor-not-allowed"
        >
          {loading ? 'Génération...' : 'Générer l\'infra'}
        </button>

        {loading && <LoadingSpinner />}

        {error && !loading && (
          <div className="mt-8 p-6 bg-red-100 border-2 border-red-400 text-red-700 rounded-xl">
            <strong>Erreur :</strong> {error}
          </div>
        )}

        {result && (
          <div className="mt-12 space-y-6">
            {/* Message principal */}
            <div className={`p-6 border-2 rounded-xl ${result.success ? 'bg-green-100 border-green-400 text-green-700' : 'bg-red-100 border-red-400 text-red-700'}`}>
              <strong>{result.message}</strong>
            </div>

            {/* Rapports sécurité (inchangé) */}
            {result.security_report?.dangerous_requests?.length ? (
              <div className="p-6 bg-red-100 border-2 border-red-500 rounded-xl">
                <h3 className="text-xl font-bold text-red-800 mb-4">
                  Demandes bloquées ({result.security_report.dangerous_requests.length})
                </h3>
                {result.security_report.dangerous_requests.map((d, i) => (
                  <div key={i} className="mb-3 p-4 bg-white rounded-lg">
                    <div className="font-bold text-red-600">Demande : {d.requested}</div>
                    <div className="text-sm text-gray-700 mt-1">Raison : {d.reason}</div>
                    <div className="text-sm text-green-600 mt-1">Appliqué : {d.applied}</div>
                  </div>
                ))}
              </div>
            ) : null}

            {result.security_report?.violations?.length ? (
              <div className="p-6 bg-orange-100 border-2 border-orange-400 rounded-xl">
                <h3 className="text-xl font-bold text-orange-800 mb-4">
                  Alertes de sécurité ({result.security_report.violations.length})
                </h3>
                {result.security_report.violations.map((v, i) => (
                  <div key={i} className="mb-3 p-4 bg-white rounded-lg">
                    <div className="font-bold text-red-600">{v.message}</div>
                    <div className="text-sm text-gray-600 mt-1">Recommandation : {v.recommendation}</div>
                  </div>
                ))}
                <div className="mt-4 text-sm font-semibold">
                  Score de sécurité :{' '}
                  <span className={result.security_report.security_score >= 80 ? 'text-green-600' : 'text-red-600'}>
                    {result.security_report.security_score}/100
                  </span>
                </div>
              </div>
            ) : null}

            {/* Stats agrégées */}
            {result.success && stats && (
              <div className="p-8 bg-white rounded-xl shadow-lg border">
                <h3 className="text-2xl font-bold mb-6">Infrastructure détectée :</h3>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-6">
                  <div className="bg-blue-50 p-4 rounded-lg">
                    <div className="text-sm text-gray-600">Provider(s)</div>
                    <div className="text-2xl font-bold text-blue-600">{stats.providerNames}</div>
                  </div>
                  <div className="bg-purple-50 p-4 rounded-lg">
                    <div className="text-sm text-gray-600">Serveurs</div>
                    <div className="text-2xl font-bold text-purple-600">{stats.totalServers}</div>
                  </div>
                  {/* ... les autres cartes inchangées ... */}
                  <div className="bg-green-50 p-4 rounded-lg">
                    <div className="text-sm text-gray-600">Bases de données</div>
                    <div className="text-2xl font-bold text-green-600">{stats.totalDatabases}</div>
                  </div>
                  <div className="bg-yellow-50 p-4 rounded-lg">
                    <div className="text-sm text-gray-600">Réseaux</div>
                    <div className="text-2xl font-bold text-yellow-600">{stats.totalNetworks}</div>
                  </div>
                  <div className="bg-red-50 p-4 rounded-lg">
                    <div className="text-sm text-gray-600">Load Balancers</div>
                    <div className="text-2xl font-bold text-red-600">{stats.totalLBs}</div>
                  </div>
                  <div className="bg-indigo-50 p-4 rounded-lg">
                    <div className="text-sm text-gray-600">Security Groups</div>
                    <div className="text-2xl font-bold text-indigo-600">{stats.totalSGs}</div>
                  </div>
                </div>
              </div>
            )}

            {/* ──── NOUVEAU : AFFICHAGE CODE AVEC ONGLETS ──── */}
            {result.success && result.terraform_code && result.terraform_code !== 'BLOCKED' && (
              <div className="p-8 bg-white rounded-xl shadow-lg border">
                <h3 className="text-2xl font-bold mb-4">Code Terraform généré</h3>

                {/* Onglets providers (seulement si > 1) */}
                {hasMultipleProviders && (
                  <div className="flex flex-wrap gap-2 mb-5 border-b pb-2">
                    {providerKeys.map((key) => (
                      <button
                        key={key}
                        onClick={() => setSelectedProvider(key)}
                        className={`
                          px-5 py-2.5 rounded-t-lg font-medium transition
                          ${selectedProvider === key
                            ? 'bg-blue-600 text-white shadow'
                            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'}
                        `}
                      >
                        {key.toUpperCase()}
                      </button>
                    ))}
                  </div>
                )}

                {/* Titre du bloc code */}
                <div className="flex justify-between items-center mb-3">
                  <h4 className="text-lg font-semibold text-gray-800">
                    {hasMultipleProviders
                      ? `Terraform – ${selectedProvider.toUpperCase()}`
                      : 'Terraform complet'}
                  </h4>

                  <div className="flex gap-3">
                    <button
                      onClick={copyToClipboard}
                      className="px-5 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition"
                    >
                      Copier
                    </button>
                    <button
                      onClick={downloadTerraform}
                      className="px-5 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg font-medium transition"
                    >
                      Télécharger .tf
                    </button>
                  </div>
                </div>

                {/* Le code */}
                <pre className="bg-gray-900 text-green-300 p-6 rounded-lg overflow-auto text-sm font-mono leading-relaxed max-h-[500px] border border-gray-700">
                  {getDisplayCode()}
                </pre>
              </div>
            )}

            <button
              onClick={() => {
                setNeed('');
                setResult(null);
                setError('');
                setSelectedProvider('all');
              }}
              className="w-full px-8 py-4 bg-gray-200 hover:bg-gray-300 text-gray-700 rounded-xl font-semibold transition"
            >
              Nouvelle génération
            </button>
          </div>
        )}
      </div>
    </main>
  );
}
