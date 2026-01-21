import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    // Recuperation du body envoye par l'UI
    const body = await request.json();
    
    console.log('Relais vers Flask');
    console.log('Description:', body.description?.substring(0, 50) + '...');
    
    // Appel backend Flask avec transformation body.description -> phrase
    const flaskResponse = await fetch('http://localhost:5000/generate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ description: body.description }),
    });
    
    // Gestion erreur Flask
    if (!flaskResponse.ok) {
      const errorData = await flaskResponse.json().catch(() => ({}));
      console.error('Erreur Flask:', errorData);
      
      return NextResponse.json(
        { error: errorData.error || 'Erreur backend Flask' },
        { status: flaskResponse.status }
      );
    }
    
    // Recuperation reponse Flask
    const flaskData = await flaskResponse.json();
    console.log('Flask status:', flaskData.security);

    // Transformation format Flask vers format UI
    // Flask: {json, security, terraform, security_report}
    // UI: {success, infrastructure, terraform_code, message, security_report}

    // Adaptation security_report pour compatibilite UI Mariam
    // Gere 2 cas NOT_OK: dangerous_requests (proactif) et violations (score bas)
    const securityReport = flaskData.security_report 
      ? {
          violations: flaskData.security_report.violations || [],
          dangerous_requests: flaskData.security_report.dangerous_requests || [],
          total_issues: (flaskData.security_report.violations?.length || 0) + 
                        (flaskData.security_report.dangerous_requests?.length || 0),
          security_score: flaskData.security_report.score || 0
        }
      : null;

    const response = {
      success: flaskData.security === 'OK',
      infrastructure: flaskData.json,
      terraform_code: flaskData.terraform || '',
      message: flaskData.security === 'OK' 
        ? 'Infrastructure generee avec succes' 
        : 'Generation bloquee pour raisons de securite',
      security_report: securityReport,
    };
    
    return NextResponse.json(response);
    
  } catch (error: any) {
    console.error('Erreur proxy:', error.message);
    
    return NextResponse.json(
      { 
        error: error.message || 'Erreur serveur Next.js',
        details: 'Verifiez que Flask tourne sur http://localhost:5000'
      },
      { status: 500 }
    );
  }
}

// Route GET pour tester que l'API fonctionne
export async function GET() {
  return NextResponse.json({ 
    message: 'API Next.js proxy vers Flask',
    status: 'ok',
    backend: 'http://localhost:5000/generate'
  });
}