#! python
# coding: utf-8

import os, sys, time, random, json, base64
from subprocess import Popen, PIPE
from flask import (
  Flask, request, render_template, Response, logging, make_response)

app = Flask(__name__)

@app.route('/')
def index():
    return u'テスト'

@app.route('/font.css', methods=['POST'])
def fontcss():
    try:
        json_data = json.loads(request.data)
        # valid check
        if not isinstance(json_data, dict):
            raise ValueError()
        if False in {
            json_data.has_key('text'),
            json_data.has_key('fontName')
        }:
            raise ValueError()
        if False in {
            isinstance(json_data['text'], unicode),
            isinstance(json_data['fontName'], unicode)
        }:
            raise ValueError()
        
        # font_filename
        font_dir = os.path.join(os.path.dirname(__file__), 'fonts')
        font_filename = "mplus-1p-light.ttf"
        font_filepath = os.path.join(font_dir, font_filename)
        font_filepath = os.path.abspath(font_filepath)
        
        # export_filename
        tmp_dir = os.path.join(os.path.dirname(__file__), 'tmp')
        unixtime = int(time.time())
        random_str = "".join([
            random.choice("1234567890ABCDEF") for x in xrange(10)
        ])
        
        export_filename = "{unixtime}_{random_str}.ttf".format(
                      unixtime=unixtime,
                      random_str=random_str)
        export_filepath = os.path.join(tmp_dir, export_filename)
        export_filepath = os.path.abspath(export_filepath)
        
        # make script
        script = u''
        
        script += u"Open(\"%s\")\n" % font_filepath
        
        char_list = list(json_data['text'])
        for char in char_list:
            script += u"SelectMore(%s)\n" % ord(char)

        script += "SelectInvert()\n"
        script += "Clear()\n"
        script += "Generate(\"%s\")\n" % export_filepath
        script += "Quit(0)\n"
        
        fontforge = Popen(
            "/usr/bin/fontforge -lang=ff -script",
            shell=True, stdin=PIPE)
        fontforge.stdin.write(script)
        fontforge.stdin.close()
        fontforge.wait()
        
        export_data = open(export_filepath).read()
        export_base64 = base64.b64encode(export_data)
        os.remove(export_filepath)

    except ValueError:
        response = Response()
        response.status_code = 400
        return response
    except IOError:
        response = Response()
        response.status_code = 404
        return response
  
    response = make_response(render_template(
      'font.css',
      export_base64=export_base64,
      font_family='testFont'))
    response.headers['Access-Control-Allow-Origin']= "*"
    
    return response

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
