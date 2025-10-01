// https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/cloudfront-functions.html
import cf from 'cloudfront';

const kvsHandle = cf.kvs();

async function handler(event) {
    var request = event.request;
    
    console.log('=== All Headers ===');
    for (let headerName in request.headers) {
        let headerValue = request.headers[headerName].value || 'EMPTY';
        console.log(headerName + ': "' + headerValue + '"');
    }
    
    // Get origins from KV store
    let originA = 'example.com';
    let originB = 'example.com/arizona';
    
    try {
        originA = await kvsHandle.get('origin-a-url');
        console.log('originA: "' + (originA || 'EMPTY') + '"');
        originB = await kvsHandle.get('origin-b-url');
        console.log('originB: "' + (originB || 'EMPTY') + '"');
    } catch (err) {
        console.log('KVS lookup failed:', err.message);
    }
    
    // Route Arizona users to Origin B, everyone else to Origin A
    var viewerCountry = request.headers['cloudfront-viewer-country'] ? request.headers['cloudfront-viewer-country'].value : '';
    console.log('viewerCountry: "' + (viewerCountry || 'EMPTY') + '"');
    var viewerRegion = request.headers['cloudfront-viewer-country-region-name'] ? request.headers['cloudfront-viewer-country-region-name'].value : '';
    console.log('viewerRegion: "' + (viewerRegion || 'EMPTY') + '"');
    
    if (viewerCountry === 'US' && viewerRegion === 'Arizona') {
        console.log('Redirecting Arizona user to Origin B: ' + (originB || 'EMPTY') + '"');
        return {
            statusCode: 302,
            statusDescription: 'Found',
            headers: {
                'location': { value: originB + request.uri }
            }
        };
    } else {
        console.log('Continuing to Origin A: '  + (originA || 'EMPTY') + '"');
        return request;
    }
}
