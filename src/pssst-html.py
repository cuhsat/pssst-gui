#!/usr/bin/env python
"""
Copyright (C) 2013-2015  Christian & Christian <hello@pssst.name>
Copyright (C) 2015-2016  Christian Uhsat <christian@uhsat.de>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
"""
import base64
import binascii
import json
import os
import re
import sys
import webbrowser


try:
    from pssst import Pssst, CLI
except ImportError:
    sys.exit("Requires Pssst (https://github.com/cuhsat/pssst)")


try:
    import cherrypy
except ImportError:
    sys.exit("Requires CherryPy (https://www.cherrypy.org)")


try:
    from Crypto import Random
    from Crypto.Cipher import AES
except ImportError:
    sys.exit("Requires PyCrypto (https://github.com/dlitz/pycrypto)")


__all__, __version__ = ["PssstHtml"], "0.2.0"


class PssstHtml:
    """
    Local proxy for encrypted calls.

    Methods
    -------
    call(params)
        Calls the CLI and returns the result.
    exit()
        Shuts down the proxy.
    name()
        Returns the canonical user name.
    pull()
        Overrides pull method with encoding.
    push(receiver, message)
        Overrides push method with encoding.

    """
    def __init__(self, profile, token):
        """
        Initializes the instance with the security token.

        Parameters
        ----------
        param profile : tuple
            The users profile.

        param token : Bytes
            Security token.

        Raises
        ------
        Exception
            Because the profile is required.

        """
        if not profile:
            raise Exception("Profile required")

        self.pssst = Pssst(*profile)
        self.token = token

    def __encrypt(self, text):
        """
        Returns the encrypted data.

        Parameters
        ----------
        param text : string
            Decrypted text.

        Returns
        -------
        Base64
            Encrypted data.

        """
        key, iv, size = self.token[:32], self.token[32:], AES.block_size

        data = text + (size - len(text) % size) * chr(size - len(text) % size)
        data = data.encode("utf-8")
        data = AES.new(key, AES.MODE_CBC, iv).encrypt(data)
        data = base64.b64encode(data)

        return data

    def __decrypt(self, data):
        """
        Returns the decrypted text.

        Parameters
        ----------
        param data : Base64
            Encrypted data.

        Returns
        -------
        string
            Decrypted text.

        """
        key, iv = self.token[:32], self.token[32:]

        data = base64.b64decode(data)
        data = AES.new(key, AES.MODE_CBC, iv).decrypt(data)
        data = data.decode("utf-8")
        text = data[0:-ord(data[-1])]

        return text

    def call(self, request):
        """
        Calls the CLI and returns the response.

        Parameters
        ----------
        param request : string
            Encrypted request.

        Returns
        -------
        string
            Encrypted response.

        """
        try:
            request = json.loads(self.__decrypt(request))

            method = request["method"]
            params = request["params"]

            for obj in [self, self.pssst]:
                if method in dir(obj):
                    response = json.dumps(getattr(obj, method)(*params))
                    break

        except Exception as ex:
            cherrypy.response.status = 500 # Internal Server Error
            response = str(ex)

        finally:
            return self.__encrypt(response)

    def exit(self):
        """
        Shuts down the proxy.

        """
        raise SystemExit()

    def name(self):
        """
        Returns the canonical user name.

        """
        return repr(self.pssst.user)

    def pull(self):
        """
        Overrides pull method with encoding.
        
        """
        return [data.decode("utf-8") for data in self.pssst.pull()]

    def push(self, receiver, message):
        """
        Overrides push method with encoding.
        
        """
        self.pssst.push(receiver, message.encode("utf-8"))

    call.exposed = True


def main(script, arg="62222", *args):
    """
    Usage: %s [option|port]

    Options:
      -h, --help      Shows the usage
      -l, --license   Shows the license
      -v, --version   Shows the version

    Report bugs to <christian@uhsat.de>
    """
    try:
        script = os.path.basename(script)

        if arg in ("/?", "-h", "--help", None):
            print(re.sub("(?m)^ {4}", "", main.__doc__ % script).strip())

        elif arg in ("-l", "--license"):
            print(__doc__.strip())

        elif arg in ("-v", "--version"):
            print("Pssst HTML " + __version__)

        elif arg.isdigit():
            url, host, port = "http://%s:%s/pssst#%s", "0.0.0.0", int(arg)

            tokenbin = Random.get_random_bytes(48)
            tokenhex = binascii.hexlify(tokenbin).decode("ascii")

            webbrowser.open_new_tab(url % (host, port, tokenhex))

            bower = os.path.join(os.path.dirname(__file__), "bower")
            pssst = os.path.join(os.path.dirname(__file__), "pssst")

            cherrypy.quickstart(PssstHtml(CLI.profile(), tokenbin), "/", {
                "global": {
                    "server.socket_host": host,
                    "server.socket_port": port,
                    "log.screen": False
                },
                "/bower": {
                    "tools.staticdir.on": True,
                    "tools.staticdir.dir": os.path.abspath(bower)
                },
                "/pssst": {
                    "tools.staticdir.on": True,
                    "tools.staticdir.dir": os.path.abspath(pssst),
                    "tools.staticdir.index": "index.html"
                }
            })

        else:
            print("Unknown option or invalid port: " + arg)
            print("Please use --help for help on usage.")
            return 2 # Incorrect usage

    except SystemExit:
        print("Exit")

    except KeyboardInterrupt:
        print("Abort")

    except Exception as ex:
        return "Error: %s" % ex


if __name__ == "__main__":
    sys.exit(main(*sys.argv))
