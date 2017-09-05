from flask import Flask
app = Flask('api')

@app.route('/')
def helloworld():
    return "YAY IT WORKS"


@app.route('/api/test')
def apitest():
    return "THIS WORKS TOO"