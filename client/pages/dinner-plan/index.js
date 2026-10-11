const WXAPI = require('../../wxapi/main')

Page({
  data: {
    plan: null,
    loading: true,
    submitting: false
  },
  onShow: function() {
    this.loadPlan()
  },
  onPullDownRefresh: function() {
    this.loadPlan().finally(() => wx.stopPullDownRefresh())
  },
  loadPlan: function() {
    this.setData({ loading: true })
    return WXAPI.dinnerPlanCurrent().then(res => {
      if (res.code === 0) {
        const plan = res.data && res.data.id ? res.data : null
        if (plan) {
          plan.feeding_total = (plan.items || []).reduce((sum, item) => sum + Number(item.feeding_value || 0) * Number(item.quantity || 0), 0)
          plan.items = (plan.items || []).map(item => Object.assign({}, item, {
            cook_reward: Number(item.feeding_value || 0) * Number(item.quantity || 0)
          }))
        }
        this.setData({ plan })
      }
    }).catch(() => {
      wx.showToast({ title: '加载失败，请检查网络', icon: 'none' })
    }).finally(() => this.setData({ loading: false }))
  },
  completePlan: function() {
    this.updatePlan('completeDinnerPlan', '这顿饭已记录')
  },
  cancelPlan: function() {
    this.updatePlan('cancelDinnerPlan', '菜单已取消')
  },
  updatePlan: function(method, message) {
    if (!this.data.plan || this.data.submitting) {
      return
    }
    this.setData({ submitting: true })
    WXAPI[method](this.data.plan.id).then(res => {
      if (res.code === 0) {
        if (method === 'completeDinnerPlan') {
          const value = this.data.plan.feeding_total || 0
          wx.showToast({ title: '已记录 +' + value + ' 投喂值', icon: 'success' })
        }
        this.setData({ plan: null })
        if (method !== 'completeDinnerPlan') wx.showToast({ title: message, icon: 'success' })
      }
    }).catch(() => {
      wx.showToast({ title: '操作失败，请检查网络', icon: 'none' })
    }).finally(() => this.setData({ submitting: false }))
  },
  goChoose: function() {
    wx.switchTab({ url: '/pages/category/category' })
  }
})
