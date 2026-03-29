#  Developed by t.me/napaaextra
from aiohttp import web

routes = web.RouteTableDef()

@routes.get("/", allow_head=True)
async def root_route_handler(request):
    html_page = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>File Store Bot - Status</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap');

            body {
                font-family: 'Roboto', -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
                margin: 0;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: #333;
            }

            .container {
                text-align: center;
                padding: 40px 50px;
                border-radius: 15px;
                background: rgba(255, 255, 255, 0.9);
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.2);
                max-width: 90%;
                width: 450px;
            }

            .status-icon {
                width: 80px;
                height: 80px;
                margin-bottom: 20px;
            }

            .status-icon .circle {
                fill: #e8f5e9; /* Light green background */
                stroke: #a5d6a7;
                stroke-width: 2;
            }

            .status-icon .checkmark {
                stroke: #4CAF50; /* Darker green checkmark */
                stroke-width: 6;
                stroke-linecap: round;
                stroke-linejoin: round;
            }

            h1 {
                font-size: 2.2em;
                font-weight: 700;
                color: #2c3e50;
                margin: 0 0 10px 0;
            }

            .status-message {
                font-size: 1.2rem;
                color: #555;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 8px;
            }
            
            .status-indicator {
                font-weight: bold;
                color: #4CAF50;
            }

            .pulsing-dot {
                display: inline-block;
                width: 10px;
                height: 10px;
                background-color: #4CAF50;
                border-radius: 50%;
                animation: pulse 1.75s infinite cubic-bezier(0.66, 0, 0, 1);
            }

            @keyframes pulse {
                0% {
                    transform: scale(0.95);
                    box-shadow: 0 0 0 0 rgba(76, 175, 80, 0.7);
                }
                70% {
                    transform: scale(1);
                    box-shadow: 0 0 0 10px rgba(76, 175, 80, 0);
                }
                100% {
                    transform: scale(0.95);
                    box-shadow: 0 0 0 0 rgba(76, 175, 80, 0);
                }
            }

            .footer-text {
                font-size: 0.85rem;
                color: #999;
                margin-top: 30px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <svg class="status-icon" viewBox="0 0 52 52">
                <circle class="circle" cx="26" cy="26" r="25"/>
                <path class="checkmark" d="M14 27l5.917 4.917L38 18"/>
            </svg>
            <h1>File Store Bot</h1>
            <p class="status-message">
                Service is <span class="status-indicator">Online</span>
                <span class="pulsing-dot"></span>
            </p>
            <p class="footer-text">This page confirms that the bot is running smoothly.</p>
        </div>
    </body>
    </html>
    """
    return web.Response(text=html_page, content_type="text/html")
