// Minimalny Cloudflare Worker (Edge API) — działa w >300 lokalizacjach na świecie
// bez własnego serwera (serverless).

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);

    // Prosty endpoint zdrowia do weryfikacji wdrożenia przez CI/CD
    if (url.pathname === "/health") {
      return Response.json({
        status: "ok",
        service: "wskz-cicd-worker-demo",
        timestamp: new Date().toISOString(),
        colo: request.cf?.colo ?? "local",
      });
    }

    // Domyślna odpowiedź API
    return Response.json({
      message: "Cześć z Cloudflare Workers! Wdrożono automatycznie przez CI/CD.",
      path: url.pathname,
      endpoints: ["/", "/health"],
    });
  },
};
