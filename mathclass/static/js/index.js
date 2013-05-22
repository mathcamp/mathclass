function renderPage() {
    $('#page-content').html('<div style="text-align:center"><i class="icon-spinner icon-spin icon-3x"></i></div>');
    var url = window.location.hash;
    if (url.length > 0 && url[0] === '#') {
        url = url.substring(1);
    }
    $.get('_fragment/' + url, {}, 
    function(data) {
        $('#page-content').html(data);
    }).fail(function (){
        $('#page-content').html('<div class="alert alert-block alert-error">Error loading page</div>');
    });
}

var announceIndex = 0;
function announce(msg, level, duration) {
  var div = $('<div class="alert alert-block">' + msg + '</div>');
  if (duration !== undefined) {
    var id = 'announcement-' + announceIndex++;
    div.attr('id', id);
    setTimeout(function() {
        $('#' + id).fadeOut(400, function() {$(this).remove();});
    }, duration);
  } else {
    div.prepend($('<button type="button" class="close" data-dismiss="alert">&times;</button>'));
  }
  div.addClass('alert-' + level);
  $('#announcements').append(div);
}

$(function() {
    $(window).on('hashchange', renderPage);
    renderPage();
});
