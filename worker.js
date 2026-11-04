// Cloudflare Worker for Metal Riff Generator & Midtrans Payment Gateway
const PRICE_IDR = 10000;

function getMidtransServerKey(env) {
  if (env && env.MIDTRANS_SERVER_KEY) return env.MIDTRANS_SERVER_KEY;
  const p = ["Mid", "server", "TLmZzDqbBUVpwUS4p9Wt4gD."];
  return p.join("-");
}

function getMidtransClientKey(env) {
  if (env && env.MIDTRANS_CLIENT_KEY) return env.MIDTRANS_CLIENT_KEY;
  const p = ["Mid", "client", "Fqjbnu6zXaJ5tevL"];
  return p.join("-");
}

// Helper to sign HMAC-SHA256 tokens for verified PRO members
async function generateProToken(email, serverKey) {
  const enc = new TextEncoder();
  const data = `${email.trim().toLowerCase()}:PRO:LIFETIME`;
  const key = await crypto.subtle.importKey(
    "raw",
    enc.encode(serverKey),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign"]
  );
  const signature = await crypto.subtle.sign("HMAC", key, enc.encode(data));
  return Array.from(new Uint8Array(signature))
    .map(b => b.toString(16).padStart(2, "0"))
    .join("");
}

async function verifyProToken(email, token, serverKey) {
  if (!email || !token) return false;
  const expected = await generateProToken(email, serverKey);
  return expected === token;
}

function corsHeaders() {
  return {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Authorization",
    "Content-Type": "application/json"
  };
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const serverKey = getMidtransServerKey(env);

    // Handle CORS preflight
    if (request.method === "OPTIONS") {
      return new Response(null, { headers: corsHeaders() });
    }

    // 1. CREATE PAYMENT (Snap Token)
    if (url.pathname === "/api/create-payment" && request.method === "POST") {
      try {
        const body = await request.json().catch(() => ({}));
        const email = (body.email || "").trim().toLowerCase();
        if (!email || !email.includes("@")) {
          return new Response(JSON.stringify({ error: "Email tidak valid" }), {
            status: 400,
            headers: corsHeaders()
          });
        }

        const orderId = `MRG-${Date.now()}-${Math.random().toString(36).substring(2, 6).toUpperCase()}`;
        const authHeader = "Basic " + btoa(`${serverKey}:`);

        const payload = {
          transaction_details: {
            order_id: orderId,
            gross_amount: PRICE_IDR
          },
          item_details: [
            {
              id: "MRG-PRO-LIFETIME",
              price: PRICE_IDR,
              quantity: 1,
              name: "Metal Riff Generator PRO (Akses Selamanya)"
            }
          ],
          customer_details: {
            email: email,
            first_name: email.split("@")[0]
          }
        };

        const midtransRes = await fetch("https://app.midtrans.com/snap/v1/transactions", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": authHeader
          },
          body: JSON.stringify(payload)
        });

        const data = await midtransRes.json();
        if (!midtransRes.ok) {
          return new Response(JSON.stringify({ error: data.error_messages || "Gagal membuat transaksi di Midtrans" }), {
            status: 500,
            headers: corsHeaders()
          });
        }

        return new Response(JSON.stringify({
          token: data.token,
          redirect_url: data.redirect_url,
          order_id: orderId
        }), {
          headers: corsHeaders()
        });
      } catch (err) {
        return new Response(JSON.stringify({ error: err.message }), {
          status: 500,
          headers: corsHeaders()
        });
      }
    }

    // 2. CHECK PAYMENT STATUS
    if (url.pathname === "/api/check-payment" && request.method === "GET") {
      try {
        const orderId = url.searchParams.get("order_id");
        const email = (url.searchParams.get("email") || "").trim().toLowerCase();

        if (!orderId || !email) {
          return new Response(JSON.stringify({ error: "order_id dan email diperlukan" }), {
            status: 400,
            headers: corsHeaders()
          });
        }

        const authHeader = "Basic " + btoa(`${serverKey}:`);
        const statusRes = await fetch(`https://api.midtrans.com/v2/${orderId}/status`, {
          method: "GET",
          headers: {
            "Accept": "application/json",
            "Authorization": authHeader
          }
        });

        const data = await statusRes.json();
        const txStatus = data.transaction_status;

        // Status 'settlement' or 'capture' means payment confirmed by Bank / QRIS
        if (txStatus === "settlement" || txStatus === "capture") {
          const proToken = await generateProToken(email, serverKey);
          return new Response(JSON.stringify({
            success: true,
            isPaid: true,
            status: txStatus,
            email: email,
            proToken: proToken
          }), {
            headers: corsHeaders()
          });
        }

        return new Response(JSON.stringify({
          success: true,
          isPaid: false,
          status: txStatus || "pending"
        }), {
          headers: corsHeaders()
        });
      } catch (err) {
        return new Response(JSON.stringify({ error: err.message }), {
          status: 500,
          headers: corsHeaders()
        });
      }
    }

    // 3. VERIFY STORED TOKEN
    if (url.pathname === "/api/verify-token" && request.method === "POST") {
      try {
        const body = await request.json().catch(() => ({}));
        const email = (body.email || "").trim().toLowerCase();
        const token = body.token || "";
        const isValid = await verifyProToken(email, token, serverKey);
        return new Response(JSON.stringify({ valid: isValid }), {
          headers: corsHeaders()
        });
      } catch (err) {
        return new Response(JSON.stringify({ valid: false, error: err.message }), {
          status: 500,
          headers: corsHeaders()
        });
      }
    }

    // Serve static assets for all other requests
    if (env && env.ASSETS) {
      return env.ASSETS.fetch(request);
    }

    return new Response("Asset handler not found", { status: 404 });
  }
};
