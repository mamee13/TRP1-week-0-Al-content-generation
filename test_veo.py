from google.genai import types
try:
    c = types.GenerateVideoConfig()
    print("GenerateVideoConfig exists")
except AttributeError:
    print("AttributeError: GenerateVideoConfig DOES NOT EXIST")

try:
    c = types.GenerateVideosConfig()
    print("GenerateVideosConfig exists")
except AttributeError:
    print("AttributeError: GenerateVideosConfig DOES NOT EXIST")
