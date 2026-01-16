   'use client';

import { useState } from 'react';

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
  ansible_playbook: string; //  AJOUTÉ
  message: string;
  security_report?: {
    violations: Array<{
      rule: string;
      severity: string;
      message: string;
      recommendation: string;
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
  const [selectedFormat, setSelectedFormat] = useState<'terraform' | 'ansible'>('terraform'); //  AJOUTÉ

  const handleGenerate = async () => {
    if (!need.trim()) {
      alert('Décris ton besoin d\'infrastructure !');
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
    } catch (err: any) {
      setError(err.message || 'Une erreur est survenue');
      console.error('Erreur:', err);
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = () => {
    const code = selectedFormat === 'terraform' ? result?.terraform_code : result?.ansible_playbook;
    if (code) {
      navigator.clipboard.writeText(code)
        .then(() => {
          alert(`Code ${selectedFormat === 'terraform' ? 'Terraform' : 'Ansible'} copié dans le presse-papier !`);
        })
        .catch((err) => {
          console.error('Erreur lors de la copie:', err);
          alert(' Impossible de copier. Essayez manuellement.');
        });
    }
  };

  const downloadTerraform = () => {
    if (result?.terraform_code) {
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
        alert(' Fichier main.tf téléchargé avec succès !');
      } catch (err) {
        console.error('Erreur lors du téléchargement:', err);
        alert(' Impossible de télécharger le fichier.');
      }
    }
  };

  //  NOUVELLE FONCTION : Télécharger Ansible
  const downloadAnsible = () => {
    if (result?.ansible_playbook) {
      try {
        const blob = new Blob([result.ansible_playbook], { type: 'text/yaml;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = 'playbook.yml';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
        alert('Fichier playbook.yml téléchargé avec succès !');
      } catch (err) {
        console.error('Erreur lors du téléchargement:', err);
        alert(' Impossible de télécharger le fichier.');
      }
    }
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
           Planificateur d'architectures sécurisées multi-cloud
        </h1>
        <p className="text-xl text-gray-600 mb-10">
          Décris ton besoin en langage naturel et on génère Terraform + Ansible + sécurité
        </p>

        <textarea
          value={need}
          onChange={(e) => setNeed(e.target.value)}
          placeholder="Exemple : J'ai besoin de 3 environnements (dev, staging, prod) avec un cluster Kubernetes HA sur AWS et Azure, VPC peering, bastion SSH, WAF, zero-trust, monitoring Prometheus+Grafana..."
          className="w-full h-64 p-6 text-lg border-2 border-gray-300 rounded-xl focus:border-blue-600 focus:outline-none resize-none font-mono"
          disabled={loading}
        />

        <button
          onClick={handleGenerate}
          disabled={loading || !need.trim()}
          className="mt-8 px-12 py-5 bg-blue-600 hover:bg-blue-700 text-white text-xl font-semibold rounded-xl shadow-lg transition transform hover:scale-105 disabled:bg-gray-400 disabled:cursor-not-allowed disabled:transform-none"
        >
          {loading ? '⏳ Génération...' : ' Générer l\'infra'}
        </button>

        {error && (
          <div className="mt-8 p-6 bg-red-100 border-2 border-red-400 text-red-700 rounded-xl">
            <strong> Erreur :</strong> {error}
          </div>
        )}

        {result && (
          <div className="mt-12 space-y-6">
            <div className="p-6 bg-green-100 border-2 border-green-400 text-green-700 rounded-xl">
              <strong> {result.message}</strong>
            </div>

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

            <div className="p-8 bg-white rounded-xl shadow-lg border">
              <h3 className="text-2xl font-bold mb-6"> Infrastructure détectée :</h3>
              
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

            {/*  NOUVEAU : TOGGLE TERRAFORM / ANSIBLE */}
            <div className="p-8 bg-white rounded-xl shadow-lg border">
              <div className="mb-6">
                <h3 className="text-2xl font-bold mb-4"> Code généré :</h3>
                
                {/* Boutons de sélection */}
                <div className="flex gap-3 mb-4">
                  <button
                    onClick={() => setSelectedFormat('terraform')}
                    className={`flex-1 px-6 py-3 rounded-lg font-semibold transition-all ${
                      selectedFormat === 'terraform'
                        ? 'bg-purple-600 text-white shadow-lg'
                        : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                    }`}
                  >
                     Terraform
                  </button>
                  <button
                    onClick={() => setSelectedFormat('ansible')}
                    className={`flex-1 px-6 py-3 rounded-lg font-semibold transition-all ${
                      selectedFormat === 'ansible'
                        ? 'bg-orange-600 text-white shadow-lg'
                        : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                    }`}
                  >
                     Ansible
                  </button>
                </div>

                {/* Boutons d'action */}
                <div className="flex gap-3 mb-4">
                  <button
                    onClick={copyToClipboard}
                    className="flex-1 px-5 py-2.5 bg-blue-500 hover:bg-blue-600 active:bg-blue-700 text-white rounded-lg font-semibold transition-all duration-200 flex items-center justify-center gap-2 shadow-md hover:shadow-lg"
                    title="Copier dans le presse-papier"
                  >
                    <span className="text-lg"></span>
                    <span>Copier</span>
                  </button>
                  
                  {selectedFormat === 'terraform' ? (
                    <button
                      onClick={downloadTerraform}
                      className="flex-1 px-5 py-2.5 bg-purple-500 hover:bg-purple-600 active:bg-purple-700 text-white rounded-lg font-semibold transition-all duration-200 flex items-center justify-center gap-2 shadow-md hover:shadow-lg"
                      title="Télécharger main.tf"
                    >
                      <span className="text-lg">⬇️</span>
                      <span>Télécharger .tf</span>
                    </button>
                  ) : (
                    <button
                      onClick={downloadAnsible}
                      className="flex-1 px-5 py-2.5 bg-orange-500 hover:bg-orange-600 active:bg-orange-700 text-white rounded-lg font-semibold transition-all duration-200 flex items-center justify-center gap-2 shadow-md hover:shadow-lg"
                      title="Télécharger playbook.yml"
                    >
                      <span className="text-lg">⬇️</span>
                      <span>Télécharger .yml</span>
                    </button>
                  )}
                </div>
              </div>
              
              {/* Affichage du code */}
              <pre className="bg-gray-900 text-green-400 p-6 rounded-lg overflow-auto text-sm font-mono leading-relaxed max-h-96">
                {selectedFormat === 'terraform' ? result.terraform_code : result.ansible_playbook}
              </pre>
            </div>

            <button
              onClick={() => {
                setNeed('');
                setResult(null);
                setError('');
                setSelectedFormat('terraform');
              }}
              className="w-full px-8 py-4 bg-gray-200 hover:bg-gray-300 text-gray-700 rounded-xl font-semibold transition"
            >
              🔄 Nouvelle génération
            </button>
          </div>
        )}
      </div>
    </main>
  );
}
