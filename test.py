import google.generativeai as genai, pkg_resources, json



API_KEY = "AIzaSyASgUPnBR4YA8b09sL2dHa-D_BMZP-6_u4"



genai.configure(api_key=API_KEY)

print("google‑generativeai version:", pkg_resources.get_distribution("google-generativeai").version)



print("\nAvailable models:")

for m in genai.list_models():

    print("  →", m.name)
