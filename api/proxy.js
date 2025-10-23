export default async function handler(req, res) {
  // Настройка CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  try {
    const { method, body, headers } = req;
    // Извлекаем путь из URL (убираем /api префикс)
    const path = req.url.replace('/api', '');
    const apiUrl = `http://87.228.88.162${path}`;
    
    console.log(`Proxying ${method} ${req.url} -> ${apiUrl}`);
    
    // Удаляем host заголовок для избежания конфликтов
    const { host, ...cleanHeaders } = headers;
    
    const response = await fetch(apiUrl, {
      method,
      headers: cleanHeaders,
      body: method !== 'GET' ? JSON.stringify(body) : undefined,
    });

    const data = await response.text();
    
    res.status(response.status).send(data);
  } catch (error) {
    console.error('Proxy error:', error);
    res.status(500).json({ error: 'Proxy error: ' + error.message });
  }
}
