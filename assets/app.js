(function(){
  // ---- Mobile rail toggle ----
  var body=document.body, t=document.getElementById('railtoggle'), scrim=document.getElementById('scrim');
  function close(){body.classList.remove('nav-open');}
  t&&t.addEventListener('click',function(){body.classList.toggle('nav-open');});
  scrim&&scrim.addEventListener('click',close);

  // ---- TOC active state (scrollspy) ----
  var links=[].slice.call(document.querySelectorAll('#toc a'));
  var map={};
  links.forEach(function(a){var id=a.getAttribute('href').slice(1); map[id]=a;
    a.addEventListener('click',function(){ if(window.innerWidth<=920) setTimeout(close,120); });});
  var targets=Object.keys(map).map(function(id){return document.getElementById(id);}).filter(Boolean);

  var spy=new IntersectionObserver(function(entries){
    entries.forEach(function(e){
      if(e.isIntersecting){
        links.forEach(function(l){l.classList.remove('active');});
        var a=map[e.target.id]; if(a) a.classList.add('active');
      }
    });
  },{rootMargin:'-12% 0px -78% 0px', threshold:0});
  targets.forEach(function(el){spy.observe(el);});

  // ---- Reveal on scroll (respects reduced motion) ----
  var rm=window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if(!rm){
    var rev=[].slice.call(document.querySelectorAll('section.dz, .method, .mast'));
    rev.forEach(function(el){el.classList.add('reveal');});
    var ro=new IntersectionObserver(function(es){
      es.forEach(function(e){ if(e.isIntersecting){ e.target.classList.add('in'); ro.unobserve(e.target);} });
    },{rootMargin:'0px 0px -8% 0px', threshold:0.04});
    rev.forEach(function(el){ro.observe(el);});
    // ensure masthead shows immediately
    document.querySelector('.mast') && document.querySelector('.mast').classList.add('in');
  }
})();
