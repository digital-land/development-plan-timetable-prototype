/* global fetch */
import SelectOrNew from './modules/select-or-new'
import MultiSelect from './modules/multi-select'

function postRecordToRegister (url, data, onSuccess, onError) {
  fetch(url, {
    method: 'POST',
    body: JSON.stringify(data),
    headers: {
      'Content-Type': 'application/json'
    }
  })
    .then(response => response.json())
    .then(data => {
      if (onSuccess) {
        onSuccess(data)
      } else {
        console.log('Success:', data)
      }
    })
    .catch((error) => {
      if (onError) {
        onError(error)
      } else {
        console.error('Error:', error)
      }
    })
}

window.dptp = {
  postRecordToRegister: postRecordToRegister,
  MultiSelect: MultiSelect,
  SelectOrNew: SelectOrNew
}
