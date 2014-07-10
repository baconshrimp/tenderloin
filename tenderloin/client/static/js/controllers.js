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
      $scope.$apply(function() {
        $scope.msgs.unshift(JSON.parse(ev.data));
      });
    }
  });

}).call(angular.module('controllers', []));
