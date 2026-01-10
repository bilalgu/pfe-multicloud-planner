'use client';

import { useState } from 'react';

export default function Home() {
  const [need, setNeed] = useState('');
  const [result, setResult] = useState('');
  const [infraJson, setInfraJson] = useState('');
  const [securityResult, setSecurityResult] = useState("");
  const [terraformStatus, setTerraformStatus] = useState("");

  // Action du bouton "Générer"
  const handleGenerate = async () => {
    // Si l'utilisateur n'a rien écrit → on bloque
    if (!need.trim()) {
      alert('Décris ton besoin d’infrastructure !');
      return;
    }
    console.log('Besoin saisi :', need);
    setResult(need);

    // Message en attendant la réponse API
    setInfraJson("Analyse en cours...");
    setSecurityResult("Analyse en cours...");
    setTerraformStatus("Analyse en cours...");

    try{
      // Appel de l'API Next.js dans api/gen/route.ts
      const response = await fetch(`/api/gen?phrase=${encodeURIComponent(need)}`)

      if (!response.ok) {
        throw new Error(`API error ${response.status}`);
      }

      const data = await response.json();
      console.log("Reponse API :", data);

      // Affichage des messages
      setInfraJson(JSON.stringify(data.json, null, 2));
      setSecurityResult(data.security);
      setTerraformStatus(data.terraform);

    } catch(error) {
      console.error("Erreur durant le process:", error)
      setInfraJson("Erreur voir la console");
      setSecurityResult("Erreur");
      setTerraformStatus("Erreur");
    }
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Planificateur d’architectures sécurisées multi-cloud
        </h1>
        <p className="text-xl text-gray-600 mb-10">
          Décris ton besoin en langage naturel → on génère Terraform + Ansible + sécurité
        </p>

        <textarea
          value={need}
          onChange={(e) => setNeed(e.target.value)}
          placeholder="Exemple : J’ai besoin de 3 environnements (dev, staging, prod) avec un cluster Kubernetes HA sur AWS et Azure, VPC peering, bastion SSH, WAF, zero-trust, monitoring Prometheus+Grafana..."
          className="w-full h-64 p-6 text-lg border-2 border-gray-300 rounded-xl focus:border-blue-600 focus:outline-none resize-none font-mono"
        />

        <button
          onClick={handleGenerate}
          className="mt-8 px-12 py-5 bg-blue-600 hover:bg-blue-700 text-white text-xl font-semibold rounded-xl shadow-lg transition transform hover:scale-105"
        >
          Générer l’infra
        </button>

        {result && (
          <div className="mt-12 p-8 bg-white rounded-xl shadow-lg border">
            <h3 className="text-2xl font-bold mb-4">Ton besoin :</h3>
            <p className="text-lg whitespace-pre-wrap bg-gray-50 p-6 rounded-lg font-mono">
              {result}
            </p>
          </div>
        )}

        {/* { Affichage du JSON } */}
        { infraJson && (
          <div className="mt-6 p-4 bg-gray-100 rounded-lg border border-gray-300">
            <h3 className="text-xl font-semibold mb-2">JSON :</h3>
            <p className="text-lg whitespace-pre-wrap bg-gray-50 p-6 rounded-lg font-mono">
              { infraJson }
            </p>
          </div>
        )}

        {/* { Affichage du statut sécurité } */}
        { securityResult && (
          <div className="mt-6 p-4 bg-gray-100 rounded-lg border border-gray-300">
            <h3 className="text-xl font-semibold mb-2">Sécurité :</h3>
            <p className="text-lg whitespace-pre-wrap bg-gray-50 p-6 rounded-lg font-mono">
              { securityResult }
            </p>
          </div>
        )}

        {/* { Affichage du statut terraform } */}
        { terraformStatus && (
          <div className="mt-6 p-4 bg-gray-100 rounded-lg border border-gray-300">
            <h3 className="text-xl font-semibold mb-2">Terraform :</h3>
            <p className="text-lg whitespace-pre-wrap bg-gray-50 p-6 rounded-lg font-mono">
              { terraformStatus }
            </p>

            { terraformStatus === "BLOCKED" && (
              <p className="mt-4 text-lg bg-gray-50 p-6 rounded-lg font-mono">
                Bloqué par la règle de sécurité.
              </p>
            )}
          </div>
        )}

      </div>
    </main>
  );
}