async function generateData() {
  const fileInput = document.getElementById('file');
  const model = document.getElementById('model').value;
  const samples = document.getElementById('samples').value;
  const outputFormat = document.getElementById('format').value;
  const message = document.getElementById('message');
  const downloadLink = document.getElementById('download-link');
  const downloadBtn = document.getElementById('downloadBtn');

  const file = fileInput.files[0];
  if (!file) {
    message.innerText = 'Please upload a CSV file.';
    return;
  }

  message.innerText = 'Generating data...';

  const formData = new FormData();
  formData.append('file', file);
  formData.append('model', model);
  formData.append('samples', samples);
  formData.append('output_format', outputFormat);

  try {
    const response = await fetch('/generate_data', {
      method: 'POST',
      body: formData,
    });

    if (response.ok) {
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      downloadBtn.href = url;
      downloadBtn.download = `synthetic_data.${outputFormat}`;
      downloadLink.style.display = 'block';
      message.innerText = 'Data generated successfully!';
    } else {
      message.innerText = 'Error generating data.';
      downloadLink.style.display = 'none';
    }
  } catch (error) {
    message.innerText = 'Failed to generate data. Please try again.';
    console.error(error);
  }
}
