Add-Type -AssemblyName System.IO.Compression.FileSystem

$source = 'C:\Users\nouam\Downloads\ONDA_Projet_Sauvegarde\report\ONDA_Risk_Intelligence_CyberRange_Defense.pptx'
$temp = "$source.morph.tmp"

if (Test-Path -LiteralPath $temp) {
  Remove-Item -LiteralPath $temp -Force
}

$inputZip = [System.IO.Compression.ZipFile]::OpenRead($source)
$outputZip = [System.IO.Compression.ZipFile]::Open($temp, [System.IO.Compression.ZipArchiveMode]::Create)
$utf8 = New-Object System.Text.UTF8Encoding($false)
$transition = '<mc:AlternateContent xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006"><mc:Choice xmlns:p159="http://schemas.microsoft.com/office/powerpoint/2015/09/main" Requires="p159"><p:transition spd="slow" advClick="1"><p159:morph option="byObject" /></p:transition></mc:Choice><mc:Fallback><p:transition spd="slow" advClick="1"><p:fade /></p:transition></mc:Fallback></mc:AlternateContent>'
$count = 0

try {
  foreach ($entry in $inputZip.Entries) {
    $newEntry = $outputZip.CreateEntry($entry.FullName, [System.IO.Compression.CompressionLevel]::Optimal)
    $outStream = $newEntry.Open()
    try {
      $isSlide = $entry.FullName -match '^ppt/slides/slide(\d+)\.xml$'
      if ($isSlide -and [int]$Matches[1] -gt 1) {
        $reader = New-Object System.IO.StreamReader($entry.Open(), $utf8)
        try { $xml = $reader.ReadToEnd() } finally { $reader.Close() }
        $xml = [regex]::Replace($xml, '(?s)<p:transition\b[^>]*>\s*<p:morph\b[^>]*/>\s*</p:transition>', '')
        $xml = [regex]::Replace($xml, '(?s)<mc:AlternateContent\b[^>]*>.*?</mc:AlternateContent>', '')
        $xml = $xml -replace '</p:sld>$', "$transition</p:sld>"
        $bytes = $utf8.GetBytes($xml)
        $outStream.Write($bytes, 0, $bytes.Length)
        $count++
      } else {
        $inStream = $entry.Open()
        try { $inStream.CopyTo($outStream) } finally { $inStream.Close() }
      }
    } finally {
      $outStream.Close()
    }
  }
} finally {
  $outputZip.Dispose()
  $inputZip.Dispose()
}

Move-Item -LiteralPath $temp -Destination $source -Force
Write-Output "Added Morph transitions to $count slides."
