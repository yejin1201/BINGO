from flask import Flask, request, jsonify
import requests
import urllib.parse


app = Flask(__name__)

apikey = '7fd3ff94eb8741edaaca'
base_url = 'http://openapi.foodsafetykorea.go.kr/api/'

@app.route('/search_recipe', methods=['GET'])
def search_recipe():
    ingredient = request.args.get('ingredient', '')

    if not ingredient:
        return jsonify({"error": "No ingredient provided"}), 400

    # URL 인코딩 처리
    encoded_ingredient = urllib.parse.quote(ingredient)
    url = f"{base_url}{apikey}/COOKRCP01/json/1/5/RCP_NM={encoded_ingredient}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        jsonData = response.json()

        # 응답 확인
        print(f"Response JSON: {jsonData}")  # 디버깅용

        result = jsonData.get("COOKRCP01", {})
        code = result.get("RESULT", {}).get("CODE", "")

        if code == "INFO-000":
            recipes = result.get("row", [])
            processed_recipes = []

            for recipe in recipes:
                recipe_data = {
                    'id': recipe.get('RCP_SEQ', 'N/A'),
                    'title': recipe.get('RCP_NM', 'N/A'),
                    'imageUrl': recipe.get('ATT_FILE_NO_MAIN', 'N/A'),
                    'imageUrl2': recipe.get('ATT_FILE_NO_MK', 'N/A'),
                    'description': recipe.get('INFO_ENG', 'N/A'),
                    'manualSteps': [],
                    'ingredients': recipe.get('RCP_PARTS_DTLS', 'N/A'),
                    'tip': recipe.get('RCP_NA_TIP', 'N/A'),
                }
                
                # 조리법 단계와 이미지 추가
                for i in range(1, 21):  # 20단계까지 처리
                    step_key = f'MANUAL{i:02}'
                    image_key = f'MANUAL_IMG{i:02}'
                    step = recipe.get(step_key, '').strip()
                    image = recipe.get(image_key, '').strip()
                    if step:
                        step_data = {'step': step}
                        if image:
                            step_data['image'] = image
                        recipe_data['manualSteps'].append(step_data)

                processed_recipes.append(recipe_data)
            
            return jsonify(processed_recipes)
        else:
            return jsonify({"error": "데이터를 찾을 수 없습니다."}), 404
    except requests.RequestException as e:
        return jsonify({"error": "API 요청 오류", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
