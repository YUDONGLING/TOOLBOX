addEventListener('fetch', event => {
    event.respondWith( handleRequest( event.request ) );
});

/**
 * Processes the Storaged Value from EdgeKV, Checks if it is Expired and Returns the Value.
 */
function getValue( StoragedValue ) {
    if ( StoragedValue === undefined ) {
        return { code: 404, value: '' };
    };

    var Expire = parseInt(StoragedValue.split('|', 1)[0]);

    if ( Expire === -1 || Expire > Date.now() / 1000 ) {
        return { code:   0, value: StoragedValue.slice(Expire.toString().length + 1) };
    } else {
        return { code: 404, value: '' };
    };
};

/**
 * Processes the Value to be Stored in EdgeKV, Returns the Value with Expiry Information.
 */
function setValue( Value, TTL, Expire ) {
    Value  = typeof Value  === 'string' ? Value : typeof Value === 'number' ? Value.toString() : JSON.stringify(Value);
    TTL    = typeof TTL    === 'number' ? TTL   : undefined;
    Expire = typeof Expire === 'number' ? Expire: undefined;

    if ( Expire > 0 ) {
        return `${ Expire }|${ Value }`;
    } else if ( TTL > 0 ) {
        return `${ Math.floor(Date.now() / 1000 + TTL) }|${ Value }`;
    } else {
        return `${ -1 }|${ Value }`;
    };
};

/**
 * Processes the Request, Checks the Method, Parses the Data, and Executes the Action to EdgeKV.
 * Returns the Response with the Result of the Action.
 * 
 * ! Due to the Limitations of EdgeKV and EdgeRuntime, the Following Restrictions Apply:
 * ! - The Maximum Number of Keys in a Single Request is 32 for GET and DELETE, and 16 for PUT.
 * ! - The Maximum Length of a Key is 512 Characters.
 * ! - The Maximum Length of a Value is 1MB.
 */
async function handleRequest( Request ) {
    if ( Request.method.toUpperCase() !== 'POST' ) {
            return new Response( JSON.stringify({
                'ec'  : 405, 'em': 'Method Not Allowed',
                'data': {}
            }), { status: 200, headers: { 'content-type': 'application/json', 'server': 'edge-routine' }});
    };

    var  Body  =  undefined;
    if ( Body === undefined ) { try { Body = await Request.json() } catch (e) {} };
    if ( Body === undefined ) { try { Body = Object.fromEntries(( await Request.formData() ).entries() ) } catch (e) {} };
    if ( Body === undefined ) {
            return new Response( JSON.stringify({
                'ec'  : 500, 'em': 'Internal Server Error',
                'data': {}
            }), { status: 200, headers: { 'content-type': 'application/json', 'server': 'edge-routine' }});
    };

    try {
            var EdgeKv = new EdgeKV({ namespace: Body.namespace });
    } catch (e) {
            return new Response( JSON.stringify({
                'ec'  : 500, 'em': 'Internal Server Error',
                'data': {}
            }), { status: 200, headers: { 'content-type': 'application/json', 'server': 'edge-routine' }});
    };

    switch ( Body.action.toUpperCase() ) {
        case 'GET':
            /** SAMPLE REQUEST BODY
             * {
             *    'action'   :  'GET',
             *    'namespace':  'SAMPLE-STORAGE',
             *    'payload'  : ['KEY1', 'KEY2', 'KEY3', ...]
             * }
             */
            var Promises = [];
            for ( let i = 0; i < Body.payload.length && i < 32; i++ ) {
                Promises.push(
                    Body.payload[i].toString().length > 512 ?   { code: 400, value: null } :
                        EdgeKv.get( Body.payload[i].toString(), { type: 'text'           } )
                            .then ( Value => { return             getValue ( Value )     } )
                            .catch( Error => { return           { code: 500, value: null }})
                );
            };
            for ( let i = 32; i < Body.payload.length; i++ ) {
                Promises.push( { code: 429, value: null } );
            };

            var Results = {};
            await Promise.all( Promises )
                .then( Object => {
                    for ( let i = 0; i < Body.payload.length; i++ ) {
                        Results[Body.payload[i].toString()] = Object[i];
                    };
                });

            return new Response( JSON.stringify({
                'ec'  : 0, 'em': '',
                'data': Results
            }), { status: 200, headers: { 'content-type': 'application/json', 'server': 'edge-routine' }});

        case 'PUT':
            /** SAMPLE REQUEST BODY
             * {
             *    'action'   :  'PUT',
             *    'namespace':  'SAMPLE-STORAGE',
             *    'payload'  : [
             *        { key: 'KEY1', value: 'VALUE1'                     },
             *        { key: 'KEY2', value: 'VALUE2', ttl   :          0 },
             *        { key: 'KEY3', value: 'VALUE3', expire: 1700000000 },
             *        ...
             *     ]
             * }
             */
            var Promises = [];
            for ( let i = 0; i < Body.payload.length && i < 16; i++ ) {
                Promises.push(
                    Body.payload[i].key.toString().length > 512 || Body.payload[i].value.toString().length > 1048576 ?  { code: 400, value: null } :
                        EdgeKv.put( Body.payload[i].key.toString(), setValue( Body.payload[i].value, Body.payload[i].ttl, Body.payload[i].expire ) )
                               .then ( Value => { return                                                                { code:   0, value: null }})
                               .catch( Error => { return                                                                { code: 500, value: null }})
                );
            };
            for ( let i = 16; i < Body.payload.length; i++ ) {
                Promises.push( { code: 429, value: null } );
            };

            var Results = {};
            await Promise.all( Promises )
                .then( Object => {
                    for ( let i = 0; i < Body.payload.length; i++ ) {
                        Results[Body.payload[i].key.toString()] = Object[i];
                    };
                });

            return new Response( JSON.stringify({
                'ec'  : 0, 'em': '',
                'data': Results
            }), { status: 200, headers: { 'content-type': 'application/json', 'server': 'edge-routine' }});

        case 'DELETE':
            /** SAMPLE REQUEST BODY
             * {
             *    'action'   :  'DELETE',
             *    'namespace':  'SAMPLE-STORAGE',
             *    'payload'  : ['KEY1', 'KEY2', 'KEY3', ...]
             * }
             */
            var Promises = [];
            for ( let i = 0; i < Body.payload.length && i < 32; i++ ) {
                Promises.push(
                    Body.payload[i].toString().length > 512 ?    { code: 400, value: null } :
                        EdgeKv.delete( Body.payload[i].toString() )
                               .then ( Value => { return Value ? { code:   0, value: null } :
                                                                 { code: 404, value: null }})
                               .catch( Error => { return         { code: 500, value: null }})
                );
            };
            for ( let i = 32; i < Body.payload.length; i++ ) {
                Promises.push( { code: 429, value: null } );
            };

            var Results = {};
            await Promise.all( Promises )
                .then( Object => {
                    for ( let i = 0; i < Body.payload.length; i++ ) {
                        Results[Body.payload[i].toString()] = Object[i];
                    };
                });

            return new Response( JSON.stringify({
                'ec'  : 0, 'em': '',
                'data': Results
            }), { status: 200, headers: { 'content-type': 'application/json', 'server': 'edge-routine' }});

        default:
            return new Response( JSON.stringify({
                'ec'  : 500, 'em': 'Internal Server Error',
                'data': {}
            }), { status: 200, headers: { 'content-type': 'application/json', 'server': 'edge-routine' }});
    };
};
