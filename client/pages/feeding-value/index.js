const WXAPI = require('../../wxapi/main')

Page({
  data: {
    balances: [],
    entries: [],
    rewards: [],
    rewardName: '',
    rewardCost: '',
    saving: false
  },
  onShow: function() {
    this.loadSummary()
  },
  onPullDownRefresh: function() {
    this.loadSummary().finally(() => wx.stopPullDownRefresh())
  },
  loadSummary: function() {
    return WXAPI.feedingValueSummary().then(res => {
      if (res.code === 0) {
        const entries = res.data.entries || []
        entries.forEach(entry => {
          entry.timeLabel = (entry.created_at || '').replace('T', ' ').slice(0, 16)
        })
        this.setData({
          balances: res.data.balances || [],
          entries,
          rewards: res.data.rewards || []
        })
      }
    }).catch(() => wx.showToast({ title: '加载失败，请检查网络', icon: 'none' }))
  },
  updateRewardName: function(e) {
    this.setData({ rewardName: e.detail.value })
  },
  updateRewardCost: function(e) {
    this.setData({ rewardCost: e.detail.value })
  },
  addReward: function() {
    const name = this.data.rewardName.trim()
    const cost = Number(this.data.rewardCost)
    if (!name || !Number.isInteger(cost) || cost <= 0) {
      wx.showToast({ title: '填写兑换内容和正整数投喂值', icon: 'none' })
      return
    }
    this.setData({ saving: true })
    WXAPI.createFeedingReward({ name, cost }).then(res => {
      if (res.code === 0) {
        this.setData({ rewardName: '', rewardCost: '' })
        return this.loadSummary()
      }
    }).catch(() => wx.showToast({ title: '保存失败，请稍后再试', icon: 'none' }))
      .finally(() => this.setData({ saving: false }))
  },
  redeem: function(e) {
    const reward = this.data.rewards[e.currentTarget.dataset.index]
    wx.showModal({
      title: '确认兑换？',
      content: '将花费 ' + reward.cost + ' 投喂值兑换「' + reward.name + '」',
      success: result => {
        if (!result.confirm) return
        WXAPI.redeemFeedingReward({ reward_id: reward.id }).then(res => {
          if (res.code === 0) {
            wx.showToast({ title: '兑换成功', icon: 'success' })
            this.loadSummary()
          }
        }).catch(() => wx.showToast({ title: '兑换失败，请稍后再试', icon: 'none' }))
      }
    })
  },
  deleteReward: function(e) {
    const reward = this.data.rewards[e.currentTarget.dataset.index]
    wx.showModal({
      title: '移除兑换内容',
      content: '移除「' + reward.name + '」？已有的兑换记录会保留。',
      success: result => {
        if (!result.confirm) return
        WXAPI.deleteFeedingReward(reward.id).then(res => {
          if (res.code === 0) this.loadSummary()
        })
      }
    })
  }
})
