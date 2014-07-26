(function() {

  this.controller('IndexCtrl', function($scope, User) {
    $scope.tenderloin = 'tenderloin';
    $scope.msgs = [];

    $scope.User = User;

    var ws = new WebSocket('ws://' + location.host + '/api/chat');

    ws.onopen = function(ev) {
      $scope.$apply(function() {
        $scope.opened = true;
        $scope.send = function(msg) {
          var obj = {
            name: "hello",
            message: msg
          }
          ws.send(JSON.stringify(obj));
          $scope.message = '';
        };
      });
    }

    ws.onmessage = function(ev) {
      var data = JSON.parse(ev.data);

      if (data.type === 'new_game') {
        (function(id) {
          var ws = new WebSocket('ws://' + location.host + '/api/table/' + id);

          ws.onopen = function(ev) {
            $scope.$apply(function() {
              $scope.game = true;
              $scope.game_id = id;
              $scope.discarded = [];
            });

            $scope.discard = function(tile) {
              ws.send(JSON.stringify({
                type: "discard",
                tile: tile
              }));
            };
          };

          ws.onmessage = function(ev) {
            var data = JSON.parse(ev.data);
            $scope.$apply(function() {
              var index;

              if (data.type === 'info') {
                $scope.hand = data.unicode;
              }
              if (data.type === 'draw') {
                $scope.hand.push(data.unicode);
              }
              if (data.type === 'end_turn') {
                $scope.cur_turn = false;
              }
              if (data.type === 'start_turn') {
                $scope.cur_turn = data.username;
              }
              if (data.type === 'discard') {
                if (data.username === User.username) {
                  index = $scope.hand.indexOf(data.unicode);
                  $scope.hand.splice(index, 1);
                }
                $scope.discarded.push({
                  tile: data.unicode,
                  username: data.username
                });
              }
            });
          };
        }).call(_, data.id);
      }

      $scope.$apply(function() {
        $scope.msgs.unshift(data);
      });
    }
  });

}).call(angular.module('controllers', []));
