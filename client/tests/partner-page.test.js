const assert = require('node:assert/strict')
const fs = require('node:fs')
const path = require('node:path')
const test = require('node:test')

const source = fs.readFileSync(path.join(__dirname, '../pages/partner/index.js'), 'utf8')
const pageBody = source.slice(source.indexOf('Page({') + 6, source.lastIndexOf('})'))
const calls = []
let subscriptionRequest = null
const wxStub = {
  showToast() {}, showLoading() {}, hideLoading() {},
  requestSubscribeMessage(options) { subscriptionRequest = options }
}
const apiStub = {
  updateDiningGroupName: payload => {
    calls.push(payload)
    return Promise.resolve({
      code: 0,
      data: {
        id: 1,
        members: [
          { user_id: 11, nickname: payload.user_id === 11 ? payload.nickname : '我的旧名' },
          { user_id: 22, nickname: payload.user_id === 22 ? payload.nickname : '搭子旧名' }
        ]
      }
    })
  }
}
const page = new Function('WXAPI', 'wx', `return ({${pageBody}})`)(apiStub, wxStub)

function createPageData() {
  return Object.assign({}, page, {
    data: { group: { members: [{ user_id: 11, nickname: '我的旧名' }, { user_id: 22, nickname: '搭子旧名' }] } },
    setData(update) {
      Object.entries(update).forEach(([key, value]) => {
        if (key === 'group.members') this.data.group.members = value
        else if (key === 'group') this.data.group = value
        else {
          const match = key.match(/^group\.members\[(\d+)\]\.editName$/)
          if (match) this.data.group.members[Number(match[1])].editName = value
          else this.data[key] = value
        }
      })
    }
  })
}

test('edits the current user and partner names independently', async () => {
  calls.length = 0
  const instance = createPageData()
  instance.editMemberName({ currentTarget: { dataset: { index: 0 } }, detail: { value: '我的新名字' } })
  instance.editMemberName({ currentTarget: { dataset: { index: 1 } }, detail: { value: '搭子新名字' } })
  assert.equal(instance.data.group.members[0].editName, '我的新名字')
  assert.equal(instance.data.group.members[1].editName, '搭子新名字')
  await instance.saveMemberName({ currentTarget: { dataset: { index: 0 } } })
  await instance.saveMemberName({ currentTarget: { dataset: { index: 1 } } })
  assert.deepEqual(calls, [
    { user_id: 11, nickname: '我的新名字' },
    { user_id: 22, nickname: '搭子新名字' }
  ])
  assert.equal(calls[0].nickname, '我的新名字')
  assert.equal(calls[1].nickname, '搭子新名字')
  assert.equal(instance.data.group.members[0].editName, '我的新名字')
  assert.equal(instance.data.group.members[1].editName, '搭子新名字')
})

test('asks WeChat for a one-time reminder only after a direct tap', () => {
  subscriptionRequest = null
  const instance = createPageData()
  instance.data.reminderTemplateId = 'template-id'
  instance.subscribeToReminders()
  assert.deepEqual(subscriptionRequest.tmplIds, ['template-id'])
  instance.data.reminderTemplateId = ''
  subscriptionRequest = null
  instance.subscribeToReminders()
  assert.equal(subscriptionRequest, null)
})
