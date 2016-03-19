/**
 * Copyright (C) 2013-2015  Christian & Christian <hello@pssst.name>
 * Copyright (C) 2015-2016  Christian Uhsat <christian@uhsat.de>
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program. If not, see <http://www.gnu.org/licenses/>.
 *
 *
 *
 * Pssst app.
 *
 * @param {Object} pssst api
 */
define(['js/pssst.api.js'], function (api) {
  /**
   * Pssst app class.
   *
   * @param {String} security token
   * @return {Object} app instance
   */
  return function (token) {
    api = api(token);
    
    /**
     * Pssst app instance.
     */
    var app = {
      /**
       * Calls the API.
       *
       * @param {String} the method
       * @param {Object} the parameters
       * @param {Function} callback
       */
      call: function call(method, params, callback) {
        api.call(method, params, function call(err, val) {
          if (!err) {
            callback(val);
          } else {
            alert(err);
          }
        });
      },

      /**
       * Shuts down the proxy.
       */
      exit: function exit() {
        app.call('exit', null, function exit() {
          clearInterval(id);
        });
      },

      /**
       * Sets the canonical user name
       */
      name: function name() {
        app.call('name', null, function name(user) {
          $('#user').text(user);
        });
      },

      /**
       * Pulls all new messages from the box.
       */
      pull: function pull() {
        app.call('pull', null, function call(messages) {
          messages.forEach(function(data) {
            $('section').append(
              '<article class="panel panel-default">'
            + '  <div class="panel-body">'
            +      data.replace('\n', '<br>')
            + '  </div>'
            + '</article>'
            );

            $('html,body').animate({scrollTop: $(document).height()}, 'slow');
          });
        });
      },

      /**
       * Pushes a new message into the box.
       */
      push: function push() {
        var line = $.trim($('input').val());

        if (line.match(/^(pssst\.)?\w{2,63}\W+.+$/)) {
          var params = line.split(/\s+/);
          var params = [params.shift(), params.join(' ')];

          app.call('push', params, function call(data) {
            $('input').val('');
          });
        }
      }
    };

    $(window).unload(function exit() { 
      app.exit();
    });

    var id = setInterval(function pull() {
      app.pull();
    }, 1000);

    $('input').on('keypress', function(e) {
      if (e.which === 13) {
        app.push();
      }
    });

    app.name();

    return this;
  };
});
