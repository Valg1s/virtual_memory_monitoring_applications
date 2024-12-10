let intervalId = null; // Declare intervalId globally

// Redirect when "separ" is clicked
document.getElementById("separ").addEventListener("click", function (event) {
    event.preventDefault();
    window.location.href = "https://www.youtube.com/watch?v=FUPJ9-6EhYU";
});

// Toggle 'clicked' class for sidebar items
document.querySelectorAll('.pcinfo__item, .main__sidebaritem').forEach(item => {
    item.addEventListener('click', function () {
        const group = item.classList.contains('pcinfo__item') ? '.pcinfo__item' : '.main__sidebaritem';
        document.querySelectorAll(group).forEach(i => i.classList.remove('clicked'));
        item.classList.add('clicked');
    });
});

const cpuLoadCtx = document.getElementById('cpuLoadChart').getContext('2d');
const cpuFreqCtx = document.getElementById('cpuFreqChart').getContext('2d');

// Update charts with new data
function updateCPUCharts(cpuLoad, cpuFreq) {
    const time = new Date().toLocaleTimeString();
    [cpuLoadChart, cpuFreqChart].forEach((chart, i) => {
        chart.data.labels.push(time);
        chart.data.datasets[0].data.push(i === 0 ? cpuLoad : cpuFreq);
        if (chart.data.labels.length > 10) {
            chart.data.labels.shift();
            chart.data.datasets[0].data.shift();
        }
        chart.update();
    });
}

// Update the data block based on API response
function update_pc_info(response) {
    const data = response.data;

    let dataBlock = document.getElementById("pcinfo_datablock");
    dataBlock.style.display = "block";

    // Check if the data is an array
    if (Array.isArray(data)) {
        // Process the data if it's an array
        dataBlock.innerHTML = ''; // Clear previous content

        const ol = document.createElement('ol');

        ol.classList.add("pcinfo__resultlist")

        data.forEach((item, index) => {
            const li = document.createElement('li');
            li.textContent = `Item ${index + 1}:`;

            const innerUl = document.createElement('ul');

            innerUl.classList.add("pcinfo__resultlist")

            // Iterate through the properties of the object
            for (const [key, value] of Object.entries(item)) {
                const innerLi = document.createElement('li');
                innerLi.textContent = `${key.charAt(0).toUpperCase() + key.slice(1)}: ${value}`;
                innerUl.appendChild(innerLi);
                innerLi.classList.add("pcinfo__resultitem")
            }

            li.appendChild(innerUl);
            ol.appendChild(li);
        });

        dataBlock.appendChild(ol);

    } else if (typeof data === 'object' && data !== null) {
        // Process the data if it's an object
        dataBlock.innerHTML = ''; // Clear previous content

        const ol = document.createElement('ol');

        // Iterate through the object's properties manually
        for (const key in data) {
            if (data.hasOwnProperty(key)) {
                const li = document.createElement('li');
                const value = data[key];

                // Display the key and value
                li.textContent = `${key.charAt(0).toUpperCase() + key.slice(1)}: ${value}`;
                li.classList.add("pcinfo__resultitem")
                ol.appendChild(li);
            }
        }
        ol.classList.add("pcinfo__resultlist")
        dataBlock.appendChild(ol);

    } else {
        // If the data is not an array or object, log an error
        const dataBlock = document.getElementById('pcinfo_datablock');
        dataBlock.innerHTML = '<p>Error: Unexpected data format received.</p>';
    }
}

axios.get(`${document.URL}get_cpu_info`).then(response => update_pc_info(response)).catch(error => {
    console.error(`Error fetching data for ${itemName}:, error`);
})

const listItems = document.querySelectorAll('.pcinfo__item');

// Add click event listener to each li
listItems.forEach(item => {
    item.addEventListener('click', () => {
        // Get the text content of the <p> tag inside each <li>
        const itemName = item.querySelector('p').textContent.trim();

        // Construct the API endpoint based on the item name
        const apiUrl = `${document.URL}get_${itemName.toLowerCase()}_info`;

        // Send GET request using axios
        axios.get(apiUrl)
            .then(response => update_pc_info(response))
            .catch(error => {
                console.error(`Error fetching data for ${itemName}:`, error);
            });
    });
});

const pc_info_button = document.getElementById('pc_info_button')

pc_info_button.addEventListener("click", () => {
   const blocks = document.querySelector(".main__datablock").querySelectorAll('div');
    blocks.forEach(div => {
        div.style.display = "none";
    });
    clearInterval(intervalId)
    // Show the CPU block
    const pc_block = document.querySelector("#pc_info_block");
    pc_block.style.display = "block";
})

function updateRamCharts(ramLoad, virtualMemoryUsage, maxRam, maxVirtualMemory) {
    const time = new Date().toLocaleTimeString();

    // Update RAM Load Chart
    ramLoadChart.data.labels.push(time);
    ramLoadChart.data.datasets[0].data.push(ramLoad);
    if (ramLoadChart.data.labels.length > 10) {
        ramLoadChart.data.labels.shift();
        ramLoadChart.data.datasets[0].data.shift();
    }
    ramLoadChart.options.scales.y.max = maxRam; // Set the maximum value dynamically
    ramLoadChart.update();

    // Update Virtual Memory Chart
    virtualMemoryFreqChart.data.labels.push(time);
    virtualMemoryFreqChart.data.datasets[0].data.push(virtualMemoryUsage);
    if (virtualMemoryFreqChart.data.labels.length > 10) {
        virtualMemoryFreqChart.data.labels.shift();
        virtualMemoryFreqChart.data.datasets[0].data.shift();
    }
    virtualMemoryFreqChart.options.scales.y.max = maxVirtualMemory; // Set the maximum value dynamically
    virtualMemoryFreqChart.update();
}

document.getElementById('ram_info_button').addEventListener('click', () => {
    document.querySelectorAll(".main__datablock div").forEach(div => div.style.display = "none");
    const ramBlock = document.getElementById("ram_block");
    ramBlock.style.display = "block";

    if (intervalId != null) clearInterval(intervalId);
    intervalId = setInterval(() => {
        axios.get(`${document.URL}get_memory_load`)
            .then(response => {
                const data = response.data;

                const ramLoadGB = (data.current_ram_usage / (1024 ** 3)).toFixed(2);
                const virtualMemoryGB = (data.current_virtual_memory_usage / (1024 ** 3)).toFixed(2);
                const maxRamGB = (data.max_ram_memory / (1024 ** 3)).toFixed(2);
                const maxVirtualMemoryGB = (data.max_virtual_memory / (1024 ** 3)).toFixed(2);

                updateRamCharts(parseFloat(ramLoadGB), parseFloat(virtualMemoryGB), parseFloat(maxRamGB), parseFloat(maxVirtualMemoryGB));            })
            .catch(error => {
                console.error("Error fetching data:", error);
            });
    }, 2000);
});



// Fetch CPU info and manage interval
document.getElementById('cpu_info_button').addEventListener('click', () => {
    document.querySelectorAll(".main__datablock div").forEach(div => div.style.display = "none");
    const cpuBlock = document.getElementById("cpu_block");
    cpuBlock.style.display = "block";

    if (intervalId != null) clearInterval(intervalId);
    intervalId = setInterval(() => {
        axios.get(`${document.URL}get_cpu_load`)
            .then(response => {
                const data = response.data;
                updateCPUCharts(data["cpu_load"], data["cpu_freq"]);
                document.querySelector("#cpu_work_time_value").textContent = data["work_time"];
            })
            .catch(error => {
                console.error("Error fetching data:", error);
            });
    }, 1000);
});
