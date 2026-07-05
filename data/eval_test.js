function findComp(root, tag) {
    if (!root) return null;
    var vnode = root[''];
    if (vnode && vnode.tag && vnode.tag.indexOf(tag) > -1) return root;
    var children = root[''];
    if (children) {
        for (var i = 0; i < children.length; i++) {
            var f = findComp(children[i], tag);
            if (f) return f;
        }
    }
    return null;
}
var detail = findComp(document.querySelector('#__nuxt').__vue__, 'TravelInternetDetail');
var dd = detail ? detail['DetailData'] : null;
JSON.stringify({found: !!detail, hasDD: !!dd, name: dd ? dd['prepaidCardName'] : 'no'})
