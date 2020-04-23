var select = document.getElementById("dropdown-menu");
for(var i = 2011; i >= 1900; --i) {
    var option = document.createElement('option');
    option.text = option.value = i;
    select.append($('<a></a>').val(p).html(p));
}
// if (dropdown) {
//     for (var i=0; i < 2;++i){
//         addOption(dropdown, "hi");
//     }
// }
//
// addOption = function(selectbox, text) {
//     var optn = document.createElement("OPTION");
//     optn.text = text;
//     optn.value = value;
//     selectbox.options.add(optn);
// }

