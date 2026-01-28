'use client';

import { useState, useEffect } from 'react';
import ErrorToast from './components/ErrorToast';
import SuccessToast from './components/SuccessToast';
import LoadingSpinner from './components/LoadingSpinner';

interface InfrastructureResult {
  success: boolean;
  infrastructure: {
    provider: string;
    servers: number;
    databases: number;
    networks: number;
    load_balancers: number;
    security_groups: number;
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

  // Auto-close toast après 5 secondes
  useEffect(() => {
    if (toast) {
      const timer = setTimeout(() => setToast(null), 5000);
      return () => clearTimeout(timer);
    }
  }, [toast]);

  const handleGenerate = async () => {
    if (!need.trim()) {
      setToast({ type: 'error', message: 'Décris ton besoin d\'infrastructure !' });
      return;
    }

    setLoading(true);
    setError('');
    setResult(null);

    try {
      const response = await fetch('/api/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ description: need }),
      });

      if (!response.ok) {
        throw new Error('Erreur lors de la génération');
      }

      const data = await response.json();
      console.log('Réponse backend:', data);
      setResult(data);
      if (data.success) {
        setToast({ type: 'success', message: 'Infrastructure générée avec succès !' });
      } else {
        setToast({ type: 'error', message: 'Génération bloquée pour raisons de sécurité' });
      }
    } catch (err: any) {
      const errorMessage = err.message || 'Une erreur est survenue';
      setError(errorMessage);
      setToast({ type: 'error', message: errorMessage });
      console.error('Erreur:', err);
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = () => {
    if (result?.terraform_code) {
      navigator.clipboard.writeText(result.terraform_code)
        .then(() => {
          setToast({ type: 'success', message: 'Code Terraform copié dans le presse-papier !' });
        })
        .catch((err) => {
          console.error('Erreur lors de la copie:', err);
          setToast({ type: 'error', message: 'Impossible de copier. Essayez manuellement.' });
        });
    }
  };

  const downloadTerraform = () => {
    if (result?.terraform_code && result.terraform_code !== 'BLOCKED') {
      try {
        const blob = new Blob([result.terraform_code], { type: 'text/plain;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = 'main.tf';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
        setToast({ type: 'success', message: 'Fichier main.tf téléchargé avec succès !' });
      } catch (err) {
        console.error('Erreur lors du téléchargement:', err);
        setToast({ type: 'error', message: 'Impossible de télécharger le fichier.' });
      }
    }
  };

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
          placeholder="Exemple : J'ai besoin de 3 serveurs web sur AWS avec une base de données MySQL"
          className="w-full h-64 p-6 text-lg border-2 border-gray-300 rounded-xl focus:border-blue-600 focus:outline-none resize-none font-mono"
          disabled={loading}
        />

        <button
          onClick={handleGenerate}
          disabled={loading || !need.trim()}
          className="mt-8 px-12 py-5 bg-blue-600 hover:bg-blue-700 text-white text-xl font-semibold rounded-xl shadow-lg transition transform hover:scale-105 disabled:bg-gray-400 disabled:cursor-not-allowed disabled:transform-none"
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
            <div className={`p-6 border-2 rounded-xl ${result.success ? 'bg-green-100 border-green-400 text-green-700' : 'bg-red-100 border-red-400 text-red-700'}`}>
              <strong>{result.message}</strong>
            </div>

            {result.security_report && result.security_report.dangerous_requests && result.security_report.dangerous_requests.length > 0 && (
              <div className="p-6 bg-red-100 border-2 border-red-500 rounded-xl">
                <h3 className="text-xl font-bold text-red-800 mb-4">
                  Demandes bloquées ({result.security_report.dangerous_requests.length})
                </h3>
                {result.security_report.dangerous_requests.map((d, i) => (
                  <div key={i} className="mb-3 p-4 bg-white rounded-lg">
                    <div className="font-bold text-red-600">Demande : {d.requested}</div>
                    <div className="text-sm text-gray-700 mt-1">
                      Raison : {d.reason}
                    </div>
                    <div className="text-sm text-green-600 mt-1">
                      Appliqué : {d.applied}
                    </div>
                  </div>
                ))}
              </div>
            )}

            {result.security_report && result.security_report.violations.length > 0 && (
              <div className="p-6 bg-orange-100 border-2 border-orange-400 rounded-xl">
                <h3 className="text-xl font-bold text-orange-800 mb-4">
                  Alertes de sécurité ({result.security_report.violations.length})
                </h3>
                {result.security_report.violations.map((v, i) => (
                  <div key={i} className="mb-3 p-4 bg-white rounded-lg">
                    <div className="font-bold text-red-600">{v.message}</div>
                    <div className="text-sm text-gray-600 mt-1">
                      Recommandation : {v.recommendation}
                    </div>
                  </div>
                ))}
                <div className="mt-4 text-sm font-semibold">
                  Score de sécurité : 
                  <span className={result.security_report.security_score >= 80 ? 'text-green-600' : 'text-red-600'}>
                    {' '}{result.security_report.security_score}/100
                  </span>
                </div>
              </div>
            )}

            {result.success && (
              <div className="p-8 bg-white rounded-xl shadow-lg border">
                <h3 className="text-2xl font-bold mb-6">Infrastructure détectée :</h3>
                
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-6">
                  <div className="bg-blue-50 p-4 rounded-lg">
                    <div className="text-sm text-gray-600">Provider</div>
                    <div className="text-2xl font-bold text-blue-600 uppercase">
                      {result.infrastructure.provider}
                    </div>
                  </div>
                  
                  <div className="bg-purple-50 p-4 rounded-lg">
                    <div className="text-sm text-gray-600">Serveurs</div>
                    <div className="text-2xl font-bold text-purple-600">
                      {result.infrastructure.servers}
                    </div>
                  </div>
                  
                  <div className="bg-green-50 p-4 rounded-lg">
                    <div className="text-sm text-gray-600">Bases de données</div>
                    <div className="text-2xl font-bold text-green-600">
                      {result.infrastructure.databases}
                    </div>
                  </div>
                  
                  <div className="bg-yellow-50 p-4 rounded-lg">
                    <div className="text-sm text-gray-600">Réseaux</div>
                    <div className="text-2xl font-bold text-yellow-600">
                      {result.infrastructure.networks}
                    </div>
                  </div>
                  
                  <div className="bg-red-50 p-4 rounded-lg">
                    <div className="text-sm text-gray-600">Load Balancers</div>
                    <div className="text-2xl font-bold text-red-600">
                      {result.infrastructure.load_balancers}
                    </div>
                  </div>
                  
                  <div className="bg-indigo-50 p-4 rounded-lg">
                    <div className="text-sm text-gray-600">Security Groups</div>
                    <div className="text-2xl font-bold text-indigo-600">
                      {result.infrastructure.security_groups}
                    </div>
                  </div>
                </div>
              </div>
            )}

            {result.success && (
              <div className="p-8 bg-white rounded-xl shadow-lg border">
                <h3 className="text-2xl font-bold mb-4">Code généré :</h3>
                
                <div className="flex gap-3 mb-4">
                  <button
                    onClick={copyToClipboard}
                    className="flex-1 px-5 py-2.5 bg-blue-500 hover:bg-blue-600 text-white rounded-lg font-semibold transition-all"
                  >
                    Copier
                  </button>
                  
                  <button
                    onClick={downloadTerraform}
                    className="flex-1 px-5 py-2.5 bg-purple-500 hover:bg-purple-600 text-white rounded-lg font-semibold transition-all"
                  >
                    Télécharger .tf
                  </button>
                </div>
                
                <pre className="bg-gray-900 text-green-400 p-6 rounded-lg overflow-auto text-sm font-mono leading-relaxed max-h-96">
                  {result.terraform_code}
                </pre>
              </div>
            )}

            <button
              onClick={() => {
                setNeed('');
                setResult(null);
                setError('');
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