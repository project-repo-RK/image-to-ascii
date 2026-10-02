// Find page elements by their IDs.
const $ = (id) => document.getElementById(id);
// Keep track of the image previews so old previews can be released.
let sourceURL, resultURL;
// Open the file picker when the upload button is clicked.
$('upload').addEventListener('click', () => $('file').click());
// Preview the selected image and clear the previous conversion.
$('file').addEventListener('change', () => {
  const file = $('file').files[0];
  if (!file) return;
  if (sourceURL) URL.revokeObjectURL(sourceURL);
  if (resultURL) URL.revokeObjectURL(resultURL);
  $('result').hidden = true;
  $('result-empty').hidden = false;
  $('download').hidden = true;
  $('filename').textContent = file.name;
  $('status').className = '';
  $('status').textContent = 'Ready to convert.';
  sourceURL = URL.createObjectURL(file);
  $('source').src = sourceURL;
  $('source').hidden = false;
  $('source-empty').hidden = true;
  $('convert').disabled = false;
});
// Send the image to Python and display the returned PNG.
$('convert').addEventListener('click', async () => {
  const file = $('file').files[0];
  if (!file) return;
  // Disable the controls until this conversion finishes.
  $('convert').disabled = true;
  $('upload').disabled = true;
  $('status').className = '';
  $('status').textContent = 'Converting…';
  $('result').hidden = true;
  $('result-empty').hidden = false;
  $('download').hidden = true;
  try {
    // Package the upload using the field name expected by app.py.
    const data = new FormData();
    data.append('image', file);
    const response = await fetch('/convert', { method: 'POST', body: data });
    // Display the server message if the image could not be converted.
    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.error || 'Conversion failed. Check the terminal for details.');
    }
    if (resultURL) URL.revokeObjectURL(resultURL);
    // Use the returned image for both the preview and the download link.
    resultURL = URL.createObjectURL(await response.blob());
    $('result').src = resultURL;
    $('result').hidden = false;
    $('result-empty').hidden = true;
    $('download').href = resultURL;
    $('download').hidden = false;
    $('status').textContent = 'Conversion complete.';
  } catch (error) {
    $('status').className = 'error';
    $('status').textContent = error.message;
  } finally {
    // Restore the controls after success or failure.
    $('convert').disabled = false;
    $('upload').disabled = false;
  }
});
