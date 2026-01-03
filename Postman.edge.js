addEventListener('fetch', event => {
    event.respondWith( handleRequest( event.request ) );
});

/**
 * Parses the Headers in the Response and Returns a Dictionary.
 */
function parseHeader( HeaderDict ) {
    var Dict = {};
    if ( HeaderDict ) {
        for (let [Key, Value] of HeaderDict.entries()) {
            Key.toLowerCase() !== 'set-cookie' ? Dict[Key] = Value : null;
        };
    };
    return Dict;
};

/**
 * Parses the `Set-Cookie` Item in the Response Header and Returns a Dictionary.
 */
function parseCookie( CookieDict, HeaderDict ) {
    var Dict = CookieDict;
    if ( HeaderDict ) {
        for (let [Key, Value] of HeaderDict.entries()) {
            Key.toLowerCase() === 'set-cookie' ? Dict[ Value.split( ';' )[0].split( '=' )[0] ] = Value.split( ';' )[0].split( '=' )[1] : null;
        };
    };
    return Dict;
};

/**
 * Parses the `Link` Item in the Response Header and Returns a Dictionary.
 */
function parseLink( LinkString ) {
    var Dict = {};
    if ( LinkString ) {
        LinkString.split( ',' ).forEach( Part => {
            var Section = Part.split(';');
            Section.length === 2 ? Dict[Section[1].replace( /rel="(.*)"/, '$1' ).trim()] = Section[0].replace( /<(.*)>/, '$1' ).trim() : null;
        });
    };
    return Dict;
};

/**
 * Encode Uint8Array to Base64 String.
 */
function encodeArrayBuffer( U8Array ) {
    var ChunkSize = 65535; // 65535 = 21845 * 3
    var Base64Parts = [];

    for ( var i = 0; i < U8Array.length; i += ChunkSize ) {
        var Chunk = U8Array.slice(i, Math.min(i + ChunkSize, U8Array.length));
        var Binary = '';
        for ( var j = 0; j < Chunk.length; j++ ) {
            Binary += String.fromCharCode( Chunk[j] );
        }
        Base64Parts.push( btoa( Binary ) );
    }
    
    return Base64Parts.join('');
};

/**
 * Processes the Request, Checks the Method, Parses the Data, and Executes the Action as a HTTP Proxy.
 * Returns the Response with the Result of the Action.
 * 
 * ! Due to the Limitations of JavaScript Fetch API, the Following Headers are Restricted:
 * ! - Expect
 * ! - Te
 * ! - Trailer
 * ! - Upgrade
 * ! - Proxy-Connection
 * ! - Connection
 * ! - Keep-Alive
 * ! - DNT
 * ! - Host
 * ! ~ And Some of Internal Headers.
 */
async function handleRequest( Request ) {
    if ( Request.method.toUpperCase() !== 'POST' ) {
        return new Response( JSON.stringify({
            'ec'  : 405, 'em': 'Method Not Allowed',
            'data': {}
        }), { status: 405, headers: { 'content-type': 'application/json', 'server': 'edge-routine' }});
    };

    var  Body  =  undefined;
    if ( Body === undefined ) { try { Body = await Request.json() } catch (e) {} };
    if ( Body === undefined ) { try { Body = Object.fromEntries(( await Request.formData() ).entries() ) } catch (e) {} };
    if ( Body === undefined ) {
        return new Response( JSON.stringify({
            'ec'  : 400, 'em': 'Bad Request',
            'data': {}
        }), { status: 400, headers: { 'content-type': 'application/json', 'server': 'edge-routine' }});
    };

    try {
        // Initialize the Fetch Option.
        var Options = {};

        Body.method && (Options.method = Body.method.toUpperCase());

        var SafeHeaders = {},
            RestrictedHeaders = new Set(['expect', 'te', 'trailer', 'upgrade', 'proxy-connection', 'connection', 'keep-alive', 'dnt', 'host']);
        Body.headers && Object.entries( Body.headers ).forEach( ([Key, Value]) => {
            var LowerCaseKey = Key.toLowerCase();
            if ( !RestrictedHeaders.has( LowerCaseKey ) ) {
                SafeHeaders[ LowerCaseKey ] = Value;
            };
        });
        Options.headers = SafeHeaders;

        Body.auth && Body.auth.type && (
            Body.auth.type.toLowerCase() === 'bearer' ? Options.headers['authorization']       = `Bearer ${ Body.auth.token }` :
            Body.auth.type.toLowerCase() === 'basic'  ? Options.headers['authorization']       = `Basic ${ btoa(`${ Body.auth.username }:${ Body.auth.password }`)}` :
            Body.auth.type.toLowerCase() === 'proxy'  ? Options.headers['proxy-authorization'] = `Basic ${ btoa(`${ Body.auth.username }:${ Body.auth.password }`)}` :
            null
        );

        Body.cookies && (
            Options.headers['cookie'] = Body.cookies.map( ([Key, Value]) => `${Key}=${Value}` ).join('; ')
        );

        Options.body = Body.data || null;
        Options.redirect = Body.allow_redirects !== undefined ? (Body.allow_redirects ? 'follow' : 'manual') : 'follow';
        Options.credentials = Body.cookies ? 'include' : 'same-origin';

        // if (Body.timeout) {
        //     Options.signal = new AbortController().signal;
        //     var TimeoutController = setTimeout(() => Options.signal.abort(), Body.timeout * 1000);
        // };

        // Operate the Fetch Request.
        var RequestStartTime  = Date.now(),
            ResponseObj = await fetch(`${ Body.url }${ Body.params ? '?' + new URLSearchParams(Body.params).toString() : ''}`, Options),
            RequestFinishTime = Date.now();

        // TimeoutController && clearTimeout(TimeoutController);

        // Process the Fetch Response.
        var Content     = '',
            ContentType = (ResponseObj.headers.get('content-type') || '').toLowerCase();

        U8Array = new Uint8Array(await ResponseObj.arrayBuffer());
        Content = encodeArrayBuffer(U8Array);

        return new Response(JSON.stringify({
            'ec'  :   0, 'em': '',
            'data': {
                '_content'             : Content,
                'ok'                   : ResponseObj.ok,
                'url'                  : ResponseObj.url,
                'next'                 : null,
                'reason'               : ResponseObj.statusText,
                'elapsed'              : (RequestFinishTime - RequestStartTime) / 1000,
                'encoding'             : (ResponseObj.headers.get('content-encoding') || (ResponseObj.headers.get('content-type') || '').includes('charset=') ? ResponseObj.headers.get('content-type').split('charset=')[1] : 'utf-8').toLowerCase(),
                'apparent_encoding'    : (ResponseObj.headers.get('content-type') || '').includes('charset=') ? ResponseObj.headers.get('content-type').split('charset=')[1].toLowerCase(): 'utf-8',
                'status_code'          : ResponseObj.status,
                'links'                : parseLink(ResponseObj.headers.get('link')),
                'headers'              : parseHeader(ResponseObj.headers),
                'cookies'              : parseCookie(Body.cookies ? Body.cookies : {}, ResponseObj.headers),
                'is_redirect'          : ResponseObj.redirected,
                'is_permanent_redirect': ResponseObj.status === 301 || ResponseObj.status === 308,
            }
        }), { status: 200, headers: { 'content-type': 'application/json', 'server': 'edge-routine' }});
    } catch (e) {
        // TimeoutController && clearTimeout( TimeoutController );
        return new Response( JSON.stringify({
            'ec'  : 500, 'em': `${ ['ValueError', 'TypeError'].includes( e.name ) ? e.name : 'Exception' }: ${ e.message }`,
            'data': {}
        }), { status: 200, headers: { 'content-type': 'application/json', 'server': 'edge-routine' }});
    };
};
