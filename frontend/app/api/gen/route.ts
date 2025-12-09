import { NextResponse } from "next/server";
import { exec } from "child_process";
import util from "util";
import fs from "fs";

const execPromise = util.promisify(exec);

// Route API : /api/gen?phrase=...
export async function GET(request: Request) {

    const { searchParams } = new URL(request.url);
    const phrase = searchParams.get("phrase") || "";

    try {
        const pythonPath = "PYTHON_PATH";
        const scriptPath = "TEST_SCRIPT_PATH";
        const checkScriptPath = "CHECK_SCRIPT_PATH";

        // Exécution du script IA Arlette
        const { stdout } = await execPromise(
            `${pythonPath} ${scriptPath} "${phrase}"`
        );
        console.log(stdout)
        const json = JSON.parse(stdout);
        
        // Sauvegarde du JSON dans un fichier temporaire
        const tmpJson = "/tmp/test-security.json";
        fs.writeFileSync(tmpJson, JSON.stringify(json));
        
        // Exécution du script python sécurité Bilal
        const { stdout: secOut } = await execPromise(
            `${pythonPath} ${checkScriptPath} ${tmpJson}`
        );

        // Si sécurité ok on génère le fichier Terraform
        let tfStatus = "NOT_GENERATED";
        if (secOut.includes("OK")) {
            console.log("Sécurité validée → Génération Terraform...");

            // Backend de Sira
            const tfScriptPath = "TF_SCRIPT_PATH";

            const { stdout: tfOut } = await execPromise(
                `${pythonPath} ${tfScriptPath} ${tmpJson}`
            );

            console.log(tfOut);
            console.log("Terraform généré avec succès")
            tfStatus = "GENERATED";
        }
        else {
            // sécurité pas ok on ne génère pas
            console.log("Sécurité non validée → Pas de génération terraform...")
            tfStatus = "BLOCKED";
        }

        // On renvoie le JSON IA + Résultat Sécurité à l'UI
        return NextResponse.json({
            json,
            security: secOut.trim(),
            terraform: tfStatus
        });

    } catch (error: any) {
        console.error("Erreur API:", error);
        return NextResponse.json({ error: "Failed to process"}, {status: 500});
    }
}