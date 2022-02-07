function onload_lang() {
  const support_lang = ["en", "ja", "zh"];
  var user_lang = navigator.language || navigator.userLanguage;
  if (!support_lang.includes(user_lang)) {
    user_lang = "en";
  }
  switch_lang(user_lang);
}

function switch_lang(lang) {
  if (lang == "en") {
    jQuery(function($) {
      $('[lang="en"]').show();
      $('[lang="ja"]').hide();
      $('[lang="zh"]').hide();
    });
  }
  else if (lang == "ja") {
    jQuery(function($) {
      $('[lang="en"]').hide();
      $('[lang="ja"]').show();
      $('[lang="zh"]').hide();
    });
  }
  else if (lang == "zh") {
    jQuery(function($) {
      $('[lang="en"]').hide();
      $('[lang="ja"]').hide();
      $('[lang="zh"]').show();
    });
  }
}