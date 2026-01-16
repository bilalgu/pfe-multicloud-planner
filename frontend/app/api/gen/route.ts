import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    // Récupérer le body de la requête frontend
    const body = await request.json();
    
    console.log('Proxy : Relais vers Flask...');
    console.log('Description:', body.description?.substring(0, 50) + '...');
    
    // APPEL AU BACKEND FLASK
    const flaskResponse = await fetch('http://localhost:5000/generate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });

    // Vérifier si Flask a répondu correctement
    if (!flaskResponse.ok) {
      const errorData = await flaskResponse.json().catch(() => ({}));
      console.error('Erreur Flask:', errorData);
      
      return NextResponse.json(
        { error: errorData.error || 'Erreur backend Flask' },
        { status: flaskResponse.status }
      );
    }

    // Récupérer la réponse de Flask
    const data = await flaskResponse.json();
    console.log('Flask a répondu avec succès');
    console.log('Infrastructure:', data.infrastructure);
    
    // Renvoyer la réponse au frontend
    return NextResponse.json(data);
    
  } catch (error: any) {
    console.error( 'Erreur proxy:', error.message);
    
    return NextResponse.json(
      { 
        error: error.message || 'Erreur serveur Next.js',
        details: 'Vérifiez que le backend Flask tourne sur http://localhost:5000'
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
