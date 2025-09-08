// GraphViz API Client
class GraphVizClient {
    constructor(baseUrl = 'http://localhost:5000') {
        this.baseUrl = baseUrl;
    }

    /**
     * Generate PNG from an existing DOT file
     * @param {string} filename - Name of the DOT file
     * @returns {Promise<Object>} - Response with output_file property
     */
    async generateFromExisting(filename) {
        const response = await fetch(`${this.baseUrl}/generate_from_existing`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ filename })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    }

    /**
     * Generate PNG from uploaded DOT file
     * @param {File} file - DOT file to upload
     * @returns {Promise<Object>} - Response with output_file property
     */
    async generateFromUpload(file) {
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await fetch(`${this.baseUrl}/generate`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    }

    /**
     * Get image URL for displaying in img tags
     * @param {string} filename - PNG filename
     * @returns {string} - Full URL to the image
     */
    getImageUrl(filename) {
        return `${this.baseUrl}/image/${filename}`;
    }

    /**
     * Get download URL for the PNG file
     * @param {string} filename - PNG filename
     * @returns {string} - Full URL for downloading
     */
    getDownloadUrl(filename) {
        return `${this.baseUrl}/download/${filename}`;
    }

    /**
     * List all available DOT files
     * @returns {Promise<Object>} - Response with dot_files array
     */
    async listDotFiles() {
        const response = await fetch(`${this.baseUrl}/list_dot_files`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    }

    /**
     * Check API health
     * @returns {Promise<Object>} - Health status
     */
    async healthCheck() {
        const response = await fetch(`${this.baseUrl}/health`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    }
}

// Usage examples:

// Example 1: Basic usage
async function example1() {
    const client = new GraphVizClient();
    
    try {
        // Generate from existing file
        const result = await client.generateFromExisting('my_graph.dot');
        
        // Display the image
        const imgElement = document.createElement('img');
        imgElement.src = client.getImageUrl(result.output_file);
        imgElement.alt = 'Generated Graph';
        document.body.appendChild(imgElement);
        
    } catch (error) {
        console.error('Error:', error);
    }
}

// Example 2: File upload
async function example2() {
    const client = new GraphVizClient();
    const fileInput = document.getElementById('fileInput');
    
    if (fileInput.files[0]) {
        try {
            const result = await client.generateFromUpload(fileInput.files[0]);
            
            // Display the image
            const imgElement = document.createElement('img');
            imgElement.src = client.getImageUrl(result.output_file);
            imgElement.alt = 'Generated Graph';
            document.body.appendChild(imgElement);
            
        } catch (error) {
            console.error('Error:', error);
        }
    }
}

// Example 3: React Hook
function useGraphViz() {
    const [client] = useState(() => new GraphVizClient());
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [imageUrl, setImageUrl] = useState('');

    const generateGraph = async (filename) => {
        setLoading(true);
        setError(null);
        
        try {
            const result = await client.generateFromExisting(filename);
            setImageUrl(client.getImageUrl(result.output_file));
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const uploadAndGenerate = async (file) => {
        setLoading(true);
        setError(null);
        
        try {
            const result = await client.generateFromUpload(file);
            setImageUrl(client.getImageUrl(result.output_file));
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    return {
        generateGraph,
        uploadAndGenerate,
        loading,
        error,
        imageUrl,
        client
    };
}

// Example 4: Vue.js Composable
function useGraphViz() {
    const client = new GraphVizClient();
    const loading = ref(false);
    const error = ref(null);
    const imageUrl = ref('');

    const generateGraph = async (filename) => {
        loading.value = true;
        error.value = null;
        
        try {
            const result = await client.generateFromExisting(filename);
            imageUrl.value = client.getImageUrl(result.output_file);
        } catch (err) {
            error.value = err.message;
        } finally {
            loading.value = false;
        }
    };

    const uploadAndGenerate = async (file) => {
        loading.value = true;
        error.value = null;
        
        try {
            const result = await client.generateFromUpload(file);
            imageUrl.value = client.getImageUrl(result.output_file);
        } catch (err) {
            error.value = err.message;
        } finally {
            loading.value = false;
        }
    };

    return {
        generateGraph,
        uploadAndGenerate,
        loading: readonly(loading),
        error: readonly(error),
        imageUrl: readonly(imageUrl),
        client
    };
}

// Export for different module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = GraphVizClient;
}

if (typeof window !== 'undefined') {
    window.GraphVizClient = GraphVizClient;
}
