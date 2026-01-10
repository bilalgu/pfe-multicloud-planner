import { NextResponse } from "next/server";
import { exec } from "child_process";
import util from "util";
import fs from "fs";

const execPromise = util.promisify(exec);

// Route API : /api/gen?phrase=...
export async function GET(request: Request) {

    const { searchParams } = new URL(request.url);
    const phrase = searchParams.get("phrase") || "";

    if (!phrase.trim()) {
        return NextResponse.json({ error: "Empty phrase" }, { status: 400 });
    }

    try {
        const pythonPath = "/home/bilal/Git/pfe-multicloud-planner/pfe-planner/bin/python3";
        const scriptPath = "/home/bilal/Git/pfe-multicloud-planner/backend/test.py";
        const checkScriptPath = "/home/bilal/Git/pfe-multicloud-planner/backend/check.py";

        // Exécution du script IA Arlette
        let json: any;

        try {
        const { stdout } = await execPromise(`${pythonPath} ${scriptPath} "${phrase}"`);
        json = JSON.parse(stdout);
        console.log(stdout)
        
        } catch (error: any) {
            return NextResponse.json( { error: "AI generation failed" }, { status: 502 } ); 

        }
        
        // Sauvegarde du JSON dans un fichier temporaire
        const tmpJson = "/tmp/test-security.json";
        fs.writeFileSync(tmpJson, JSON.stringify(json));
        
        // Exécution du script python sécurité Bilal
        let sec = "ERROR";

        try {

            const { stdout: secOut } = await execPromise(
                `${pythonPath} ${checkScriptPath} ${tmpJson}`
            );
            sec = secOut.trim(); // "OK" ou "NOT_OK"

        } catch (error: any) {

            if (error?.code === 1) {
                sec = error.stdout.trim(); // "NOT_OK"
            }
            else { throw error; }

        }


        // Si sécurité ok on génère le fichier Terraform
        let tfStatus = "NOT_GENERATED";
        if (sec === "OK") {
            console.log("Security OK → generating Terraform");

            // Backend de Sira
            const tfScriptPath = "/home/bilal/Git/pfe-multicloud-planner/backend/generate_tf.py";

            const { stdout: tfOut } = await execPromise(`${pythonPath} ${tfScriptPath} ${tmpJson}`);
            console.log(tfOut);

            tfStatus = "GENERATED";
        }
        else if (sec === "NOT_OK"){
            // sécurité pas ok, on ne génère pas du à la sécurité
            console.log("Security NOT OK → skipping Terraform")
            tfStatus = "BLOCKED";
        }
        else {
            // erreur, on ne génère pas du à l'erreur
            console.log("Security ERROR");
            tfStatus = "NOT_GENERATED";
        }

        // On renvoie le JSON IA + Résultat Sécurité à l'UI
        return NextResponse.json({
            json,
            security: sec,
            terraform: tfStatus
        });

    } catch (error: any) {
        return NextResponse.json({ error: "Failed to process"}, {status: 500});
    }
}