const WXAPI = require('../../wxapi/main')

Page({
  data: {
    group: null,
    loading: true,
    inviteToken: '',
    currentUserId: null,
    reminderTemplateId: ''
  },
  onLoad: function(options) {
    this.setData({ inviteToken: (options && options.invite_token) || '' })
  },
  onShow: function() {
    WXAPI.ensureLogin().then(() => {
      const currentUser = wx.getStorageSync('mealMateUser') || {}
      this.setData({ currentUserId: currentUser.user_id || null })
      this.loadGroup()
      this.loadReminderConfig()
    }).catch(() => this.loadGroup())
  },
  onPullDownRefresh: function() {
    this.loadGroup().finally(() => wx.stopPullDownRefresh())
  },
  loadGroup: function() {
    this.setData({ loading: true })
    return WXAPI.diningGroupCurrent().then(res => {
      if (res.code !== 0) {
        return
      }
      if (res.data && res.data.id) {
        this.setData({ group: res.data })
        return
      }
      if (this.data.inviteToken) {
        return this.joinGroup()
      }
      this.setData({ group: null })
    }).catch(() => {
      wx.showToast({ title: '加载失败，请检查网络', icon: 'none' })
    }).finally(() => this.setData({ loading: false }))
  },
  loadReminderConfig: function() {
    return WXAPI.dinnerPlanNotificationConfig().then(res => {
      this.setData({ reminderTemplateId: res.code === 0 ? (res.data.template_id || '') : '' })
    }).catch(() => this.setData({ reminderTemplateId: '' }))
  },
  subscribeToReminders: function() {
    const templateId = this.data.reminderTemplateId
    if (!templateId) return
    wx.requestSubscribeMessage({
      tmplIds: [templateId],
      success: res => {
        wx.showToast({
          title: res[templateId] === 'accept' ? '已订阅下次下单提醒' : '未开启微信提醒',
          icon: 'none'
        })
      },
      fail: () => wx.showToast({ title: '订阅失败，请稍后重试', icon: 'none' })
    })
  },
  createGroup: function() {
    WXAPI.createDiningGroup({ name: '我们的饭搭子' }).then(res => {
      if (res.code === 0) {
        this.setData({ group: res.data })
      }
    }).catch(() => {
      wx.showToast({ title: '创建失败，请检查网络', icon: 'none' })
    })
  },
  joinGroup: function() {
    return WXAPI.joinDiningGroup({ invite_token: this.data.inviteToken }).then(res => {
      if (res.code === 0) {
        this.setData({ group: res.data, inviteToken: '' })
        wx.showToast({ title: '饭搭子绑定成功', icon: 'success' })
      }
    })
  },
  editMemberName: function(e) {
    const index = e.currentTarget.dataset.index
    const members = this.data.group.members.slice()
    members[index] = Object.assign({}, members[index], { editName: e.detail.value, editingName: true })
    this.setData({ 'group.members': members })
  },
  onNameConfirm: function(e) {
    const index = e.currentTarget.dataset.index
    const member = this.data.group.members[index]
    const nickname = String(e.detail.value || '').trim()
    if (!nickname) {
      wx.showToast({ title: '名字不能为空', icon: 'none' })
      return
    }
    this.setData({ ['group.members[' + index + '].editName']: nickname })
    this.saveMemberName({ currentTarget: { dataset: { index } } })
  },
  saveMemberName: function(e) {
    const member = this.data.group.members[e.currentTarget.dataset.index]
    const nickname = String(member.editName !== undefined ? member.editName : member.nickname).trim()
    if (!nickname) {
      wx.showToast({ title: '名字不能为空', icon: 'none' })
      return
    }
    wx.showLoading({ title: '保存中' })
    WXAPI.updateDiningGroupName({ user_id: member.user_id, nickname }).then(res => {
      if (res.code === 0) {
        const drafts = this.data.group.members.map(item => ({
          editName: item.editName,
          editingName: item.editingName
        }))
        const members = (res.data.members || []).map((item, index) => Object.assign({}, item, {
          editName: index === Number(e.currentTarget.dataset.index) ? item.nickname : drafts[index].editName,
          editingName: index === Number(e.currentTarget.dataset.index) ? false : drafts[index].editingName
        }))
        this.setData({ group: Object.assign({}, res.data, { members }) })
        wx.showToast({ title: '名字已保存', icon: 'success' })
      } else {
        wx.showToast({ title: res.message || '保存失败', icon: 'none' })
      }
    }).catch(() => wx.showToast({ title: '保存失败，请稍后再试', icon: 'none' }))
      .finally(() => wx.hideLoading())
  },
  syncWechatNickname: function() {
    wx.getUserProfile({
      desc: '用于显示你在饭搭子中的名称',
      success: result => {
        const nickname = result.userInfo && result.userInfo.nickName
        if (!nickname) {
          wx.showToast({ title: '没有获取到微信昵称', icon: 'none' })
          return
        }
        WXAPI.updateProfile({ nickname }).then(res => {
          if (res.code !== 0) return
          const currentUser = wx.getStorageSync('mealMateUser') || {}
          currentUser.nickname = nickname
          wx.setStorageSync('mealMateUser', currentUser)
          this.loadGroup()
          wx.showToast({ title: '已同步微信昵称', icon: 'success' })
        })
      },
      fail: () => wx.showToast({ title: '未授权微信昵称', icon: 'none' })
    })
  },
  onShareAppMessage: function() {
    const group = this.data.group || {}
    if (!group.id) {
      return { title: '一起吃饭叭', path: '/pages/index/index' }
    }
    return {
      title: '来和我一起决定今晚吃什么',
      path: '/pages/partner/index?invite_token=' + (group.invite_token || '')
    }
  }
})
