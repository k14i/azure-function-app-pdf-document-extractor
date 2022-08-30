start:
	func start --python

start-verbose:
	func start --verbose --python

start-debug:
	func start --verbose --python --debug

start-trace:
	func start --verbose --python --debug --trace

start-profile:
	func start --verbose --python --debug --trace --profile

call-post:
	curl -X POST -H "Content-Type: application/json" -d "{\"azure_storage_container_name\":\"azure-function-app-pdf-document-extractor-source-files\", \"azure_storage_file_name\":\"sample-layout.pdf\", \"keep_local_file\":true, \"keep_blob\":true}" "http://localhost:7071/api/HttpTrigger-pdf-document-extractor"
