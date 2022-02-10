function onload_lang() {
  const support_lang = ["en", "ja", "zh"];
  var user_lang = navigator.language || navigator.userLanguage;
  if (!support_lang.includes(user_lang)) {
    user_lang = "en";
  }
  switch_lang(user_lang);
}

function switch_lang(lang) {
  $('[lang="en"]').hide();
  $('[lang="ja"]').hide();
  $('[lang="zh"]').hide();
  $('[lang="' + lang + '"]').show();
}