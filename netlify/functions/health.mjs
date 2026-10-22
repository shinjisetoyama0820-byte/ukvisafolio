
export default async function handler(request) {
  if (request.method !== "GET") {
    return new Response(
      JSON.stringify({ error: "Method not allowed" }),
      {
        status: 405,
        headers: { "Content-Type": "application/json" }
      }
    );
  }

  return new Response(
    JSON.stringify({
      service: "STRATOVISA AI CONTROL CENTER",
      status: "ok",
      message: "サーバー側の処理が正常に動作しています",
      ai_connected: false,
      timestamp: new Date().toISOString()
    }),
    {
      status: 200,
      headers: {
        "Content-Type": "application/json; charset=utf-8",
        "Cache-Control": "no-store"
      }
    }
  );
}
