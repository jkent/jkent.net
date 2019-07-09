$(function(){
  $('#header .hamburger').click(function(){
    $('#header .menu').toggleClass('visible');
  });

  const mq = window.matchMedia("(min-width: 650px)");
  mq.addListener(function(mq){
    if (mq.matches){
      $('#header .menu').removeClass('visible');
    }
  });
});

$(document).mouseup(function(e){
  var menu = $("#header .menu");
  var hamburger = $("#header .hamburger");
  if (!hamburger.is(e.target) && hamburger.has(e.target).length === 0 && !menu.is(e.target) && menu.has(e.target).length === 0) {
    menu.removeClass('visible');
  }
});
