/* global fetch, turf */
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

function getBoundingBox(features, units) {
  const _units = units || 1

  // check if features param is already a FeatureCollection
  let collection = features
  if (!Object.prototype.hasOwnProperty.call(features, 'type') || features.type !== 'FeatureCollection') {
    collection = turf.featureCollection(features)
  }

  const bufferedCollection = turf.buffer(collection, _units)
  const envelope = turf.envelope(bufferedCollection)
  return envelope.bbox
}

window.dptp = {
  getBoundingBox: getBoundingBox,
  postRecordToRegister: postRecordToRegister,
  MultiSelect: MultiSelect,
  SelectOrNew: SelectOrNew
}
