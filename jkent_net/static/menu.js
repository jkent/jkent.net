$(function(){
  $('#header .hamburger').click(function(){
    $('#header .menu').toggleClass('expanded');
  });
});

$(document).mouseup(function(e){
  var menu = $("#header .menu");
  var hamburger = $("#header .hamburger");
  if (!hamburger.is(e.target) && hamburger.has(e.target).length === 0 && !menu.is(e.target) && menu.has(e.target).length === 0) {
    menu.removeClass('expanded');
  }
});
