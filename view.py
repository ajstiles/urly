# Copyright 2008 Adam Stiles
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy 
# of the License at http://www.apache.org/licenses/LICENSE-2.0 Unless required 
# by applicable law or agreed to in writing, software distributed under the 
# License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS 
# OF ANY KIND, either express or implied. See the License for the specific 
# language governing permissions and limitations under the License.

import os
from google.appengine.ext.webapp import template

class MainView():
    """Helper method for our one-and-only template. All display goes through here"""
    @staticmethod
    def render(handler, status, urly, format, href=None):
        """Lovin my delphi-like inner functions"""
        def render_raw(handler, content_type, body):
            handler.response.headers["Content-Type"] = content_type
            handler.response.out.write(body)

        def render_main(handler, values=None):
            path = os.path.join(os.path.dirname(__file__), 'main.html')
            handler.response.out.write(template.render(path, values))

        """ We never have an error if we have an urly to show """
        if (urly is not None):
            if (format is None):
                handler.redirect(urly.href)
            elif (format == '.json'):
                render_raw(handler, "application/json", urly.to_json())
            elif (format == '.xml'):
                render_raw(handler, "application/xml", urly.to_xml())
            else:
                render_main(handler, { 'urly': urly })
        elif (status == 400):
            handler.error(status)
            if (format != '.json') and (format != '.xml'): 
                vals = { 'error_href': True, 'default_href': href }
                render_main(handler, vals)
        elif (status == 404):
            handler.error(404)
            if (format != '.json') and (format != '.xml'): 
                vals = { 'error_404': True }
                render_main(handler, vals)
        else:
            render_main(handler)
