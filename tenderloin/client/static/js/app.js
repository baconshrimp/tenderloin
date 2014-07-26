(function() {

  this.config(function($locationProvider) {
    $locationProvider.html5Mode(true);
  });

  this.config(function($routeProvider) {
    $routeProvider.when('/', {
      controller: 'IndexCtrl',
      templateUrl: '/partials/index.html'
    });

    $routeProvider.when('/404', {
      templateUrl: '/partials/404.html'
    });

    $routeProvider.otherwise({
      redirectTo: '/404'
    });
  });

  this.config(function(RestangularProvider) {
    RestangularProvider.setBaseUrl('/api');
  });

  this.config(function($httpProvider) {
    $httpProvider.interceptors.push(function($q) {
      return {
        request: function(config) {
          return config;
        },
        requestError: function(rejection) {
          return $q.reject(rejection);
        },
        response: function(response) {
          return response;
        },
        responseError: function(rejection) {
          return $q.reject(rejection);
        }
      };
    });
  });

  this.run(function($rootScope, $location, User) {
    $rootScope.User = User;

    User.getUsername().then(function(data) {
      User.username = data.username;
    });

    $rootScope.$on('$login', function(ev, username) {
      User.username = username;
    });

    $rootScope.$on('$routeChangeStart', function() {
    });

    $rootScope.$on('$routeChangeError', function() {
      $location.path('/404');
    });

    $rootScope.$on('$routeChangeSuccess', function() {
    });
  });

}).call(angular.module('tenderloin', [
  'ngRoute',
  'restangular',
  'controllers',
  'services'
]));
