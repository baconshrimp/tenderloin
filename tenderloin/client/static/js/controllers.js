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
            if (data.type === 'info') {
              $scope.$apply(function() {
                $scope.hand = data.unicode;
              });
            }
            console.log('from game: ', data);
          };
        }).call(_, data.id);
      }

      $scope.$apply(function() {
        $scope.msgs.unshift(data);
      });
    }
  });

}).call(angular.module('controllers', []));
