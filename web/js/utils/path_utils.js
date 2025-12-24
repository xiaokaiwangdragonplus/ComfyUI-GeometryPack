/**
 * ComfyUI GeomPack - Path Utilities
 * Handles base path detection and URL construction for subpath deployments
 */

// Auto-detect extension folder name (handles ComfyUI-GeometryPack or comfyui-geometrypack)
export const EXTENSION_FOLDER = (() => {
    const url = import.meta.url;
    const match = url.match(/\/extensions\/([^/]+)\//);
    return match ? match[1] : "ComfyUI-GeometryPack";
})();

/**
 * Get base path (handles subpath deployments like /dev/sd-comfyui)
 * @returns {string} Base path (e.g., '/dev/sd-comfyui' or '')
 */
export function getBasePath() {
    try {
        // First try to get from import.meta.url (JS files are always loaded via /extensions/ path)
        const jsUrl = import.meta.url;
        // Match: protocol://domain/base/path/extensions/...
        // Capture the base path (everything between domain and /extensions/)
        const jsMatch = jsUrl.match(/https?:\/\/[^\/]+(\/.*?)\/extensions\//);
        if (jsMatch && jsMatch[1]) {
            return jsMatch[1];
        }
        
        // Fallback to window.location.pathname
        const pathname = window.location.pathname;
        const extensionsIndex = pathname.indexOf('/extensions/');
        if (extensionsIndex > 0) {
            return pathname.substring(0, extensionsIndex);
        }
        
        // If pathname is like '/dev/sd-comfyui/', use it directly (remove trailing slash)
        if (pathname && pathname !== '/' && pathname.endsWith('/')) {
            return pathname.slice(0, -1);
        }
        
        return '';
    } catch (e) {
        return '';
    }
}

/**
 * Build viewer HTML URL
 * @param {string} viewerName - Name of the viewer HTML file (e.g., 'viewer_vtk.html')
 * @param {boolean} addCacheBuster - Whether to add cache buster query parameter
 * @returns {string} Full URL to the viewer HTML file
 */
export function getViewerUrl(viewerName, addCacheBuster = true) {
    const basePath = getBasePath();
    let url = `${basePath}/extensions/${EXTENSION_FOLDER}/${viewerName}`;
    if (addCacheBuster) {
        url += `?v=${Date.now()}`;
    }
    return url;
}

/**
 * Build file view URL for ComfyUI /view API
 * @param {string} filename - Name of the file
 * @param {string} type - File type ('output', 'input', 'temp')
 * @param {string} subfolder - Subfolder path (default: '')
 * @returns {string} Full URL to the file
 */
export function getFileViewUrl(filename, type = 'output', subfolder = '') {
    const basePath = getBasePath();
    return `${basePath}/view?filename=${encodeURIComponent(filename)}&type=${type}&subfolder=${encodeURIComponent(subfolder)}`;
}

/**
 * Build API endpoint URL
 * @param {string} endpoint - API endpoint path (e.g., '/upload/image', '/geompack/analyze')
 * @returns {string} Full URL to the API endpoint
 */
export function getApiUrl(endpoint) {
    const basePath = getBasePath();
    // Ensure endpoint starts with /
    const normalizedEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
    return `${basePath}${normalizedEndpoint}`;
}

/**
 * Build extension asset URL
 * @param {string} assetPath - Path to asset relative to extension root (e.g., 'js/backend_mappings.json')
 * @returns {string} Full URL to the asset
 */
export function getExtensionAssetUrl(assetPath) {
    const basePath = getBasePath();
    // Remove leading slash if present
    const normalizedPath = assetPath.startsWith('/') ? assetPath.slice(1) : assetPath;
    return `${basePath}/extensions/${EXTENSION_FOLDER}/${normalizedPath}`;
}

/**
 * Get base path for HTML files (when running in iframe)
 * This version works in HTML files where import.meta.url might not be available
 * @returns {string} Base path
 */
export function getBasePathForHTML() {
    try {
        const pathname = window.location.pathname;
        const extensionsIndex = pathname.indexOf('/extensions/');
        if (extensionsIndex > 0) {
            return pathname.substring(0, extensionsIndex);
        }
        if (pathname && pathname !== '/' && pathname.endsWith('/')) {
            return pathname.slice(0, -1);
        }
        return '';
    } catch (e) {
        return '';
    }
}

