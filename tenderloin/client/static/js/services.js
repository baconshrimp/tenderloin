(function() {

  this.factory('User', function(Restangular, $rootScope) {
    var endpoint = Restangular.all('login');

    function login(username, password) {
      return endpoint.post({
        username: username,
        password: password
      }).then(function(data) {
        $rootScope.$emit('$login');
        return data;
      });
    }

    return {
      login: login
    };
  });

}).call(angular.module('services', []));
