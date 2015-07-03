from flask import Flask
import gather_data
import parse_data

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello World!'

if __name__ == '__main__':
    gather_data.get_data()
    #parse_data.build_data()
    #app.run()