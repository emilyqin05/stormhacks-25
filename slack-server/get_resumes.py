from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/getresumes', methods=['POST'])
def get_resumes():
    user = request.form.get('user_name')
    resumes = ["Alice.pdf", "Bob.pdf", "Ethan.pdf"]
    return jsonify({
        "response_type": "in_channel",  # shows to everyone in channel
        "text": f"Here are the resumes, {user}: " + ", ".join(resumes)
    })

if __name__ == "__main__":
    app.run(port=3000)
