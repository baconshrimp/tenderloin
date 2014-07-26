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
            console.log('from game: ', data);
            $scope.$apply(function() {
              var index;

              if (data.type === 'info') {
                $scope.hand = data.unicode;
              } else if (data.type === 'draw') {
                $scope.hand.push(data.unicode);
              } else if (data.type === 'discard') {
                index = _.findIndex($scope.hand, data.unicode);
                $scope.hand = $scope.hand.splice(index, 1);
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
