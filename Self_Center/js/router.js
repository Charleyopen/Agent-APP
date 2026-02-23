/**
 * 简单 hash 路由
 */
(function (global) {
  var current = '';
  var handlers = {};

  function getHash() {
    var h = (global.location && global.location.hash) || '';
    return h.replace(/^#\/?/, '') || 'profile';
  }

  function fire(path) {
    var parts = path.split('/').filter(Boolean);
    var name = parts[0] || 'profile';
    var param = parts[1] || '';
    current = path;
    if (handlers[name]) handlers[name](param, parts);
  }

  function route(name, handler) {
    handlers[name] = handler;
  }

  function go(path) {
    if (path.charAt(0) !== '/') path = '/' + path;
    if (global.location) global.location.hash = '#/' + path.replace(/^\//, '');
    fire(getHash());
  }

  function init() {
    fire(getHash());
    if (global.addEventListener) {
      global.addEventListener('hashchange', function () {
        fire(getHash());
      });
    }
  }

  global.SelfCenter = global.SelfCenter || {};
  global.SelfCenter.router = {
    get: getHash,
    go: go,
    route: route,
    init: init,
    get current() { return current; }
  };
})(typeof window !== 'undefined' ? window : this);
