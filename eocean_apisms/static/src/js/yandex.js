jQuery(function($) {
    var waitForElementToAppear = setInterval(function() {
        if ($('.o_menu_brand').text() == 'MoceanAPI SMS') {
            $('<div />').attr('class', 'mc-consent-overlay').appendTo("body");
            $(".mc-consent-overlay").hide();
            window.cookieconsent.initialise({
                "revokeBtn": "<div class='cc-revoke cc-bottom cc-right cc-animate cc-color-override-688238583'>Data usage consent</div>",
                "palette": {
                    "popup": {
                        "background": "#000"
                    },
                    "button": {
                        "background": "#f1d600"
                    }
                },
                "position": "bottom-right",
                "type": "opt-in",
                "content": {
                    "message": "Help improve this plugin by sharing usage data!",
                    "dismiss": "Yes, I'd love to",
                    "deny": "Refuse",
                    "link": "Learn more!",
                    "allow": "Agree!",
                    "href": "https://moceanapi.com/legal/privacy"
                },
                onInitialise: function(status) {
                    if(status == cookieconsent.status.allow) myScripts();
                },
                onStatusChange: function(status) {
                    if (this.hasConsented()) myScripts();
                },
                onPopupOpen: function() {
                    $(".mc-consent-overlay").show();
                },
                onPopupClose: function() {
                    $(".mc-consent-overlay").hide();
                }
            });
            clearInterval(waitForElementToAppear);
        }
    }, 250);

});

function myScripts() {
   (function(m,e,t,r,i,k,a){m[i]=m[i]||function(){(m[i].a=m[i].a||[]).push(arguments)};
   m[i].l=1*new Date();k=e.createElement(t),a=e.getElementsByTagName(t)[0],k.async=1,k.src=r,a.parentNode.insertBefore(k,a)})
   (window, document, "script", "https://mc.yandex.ru/metrika/tag.js", "ym");

   ym(89818200, "init", {
        clickmap:true,
        trackLinks:true,
        accurateTrackBounce:true,
        webvisor:true
   });
}
